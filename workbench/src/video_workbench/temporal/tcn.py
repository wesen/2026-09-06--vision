"""Causal multi-stage frozen-feature head adapted from the ticket neural lab.

No normalization across time. Missing features mask activations at every block.
"""
from __future__ import annotations

import json
import torch
from torch import nn
from torch.nn import functional as F


class CausalBlock(nn.Module):
    def __init__(self, channels: int, dilation: int, dropout: float = 0.1):
        super().__init__()
        if channels < 1 or dilation < 1:
            raise ValueError("Channels and dilation must be positive.")
        self.left = 2 * dilation
        self.conv = nn.Conv1d(channels, channels, 3, dilation=dilation)
        self.mix = nn.Conv1d(channels, channels, 1)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        h = self.conv(F.pad(x, (self.left, 0)))
        h = self.dropout(self.mix(F.relu(h)))
        return (x + h) * mask


class Stage(nn.Module):
    def __init__(self, input_dim: int, classes: int, channels: int, layers: int):
        super().__init__()
        self.project = nn.Conv1d(input_dim, channels, 1)
        self.blocks = nn.ModuleList(
            CausalBlock(channels, 2**i) for i in range(layers)
        )
        self.head = nn.Conv1d(channels, classes, 1)

    def forward(self, x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        h = self.project(x) * mask
        for block in self.blocks:
            h = block(h, mask)
        return self.head(h) * mask


class CausalMultiStageTCN(nn.Module):
    def __init__(self, input_dim: int, classes: int, channels: int = 16,
                 layers: int = 3, stages: int = 2):
        super().__init__()
        if min(input_dim, classes, channels, layers, stages) < 1:
            raise ValueError("All dimensions and counts must be positive.")
        self.input_dim = input_dim
        self.classes = classes
        self.register_buffer("feature_mean", torch.zeros(1, input_dim, 1))
        self.register_buffer("feature_scale", torch.ones(1, input_dim, 1))
        self.receptive_field = 1 + stages * sum(2 * 2**i for i in range(layers))
        self.stages = nn.ModuleList(
            Stage(input_dim if s == 0 else classes, classes, channels, layers)
            for s in range(stages)
        )

    def forward(self, x: torch.Tensor, valid: torch.Tensor) -> torch.Tensor:
        # x: [batch, features, time]; valid: [batch, time].
        if x.ndim != 3 or x.shape[1] != self.input_dim or x.shape[2] < 1:
            raise ValueError("Invalid input shape.")
        if valid.dtype != torch.bool or valid.shape != (x.shape[0], x.shape[2]):
            raise ValueError("valid must be Boolean [batch, time].")
        if not torch.isfinite(x).all():
            raise ValueError("Features must be finite; use an explicit gap policy.")
        mask = valid[:, None, :].to(x.dtype)
        inputs, outputs = ((x - self.feature_mean) / self.feature_scale) * mask, []
        for stage in self.stages:
            logits = stage(inputs, mask)
            outputs.append(logits)
            inputs = logits.softmax(dim=1) * mask
        return torch.stack(outputs)  # [stages, batch, classes, time]


def segmentation_loss(outputs: torch.Tensor, target: torch.Tensor,
                      valid: torch.Tensor, smooth_weight: float = 0.0,
                      clip: float = 4.0, class_weight: torch.Tensor | None = None) -> torch.Tensor:
    if outputs.ndim != 4 or outputs.shape[-1] < 1:
        raise ValueError("outputs must be [stages, batch, classes, time].")
    _, batch, classes, time = outputs.shape
    if target.shape != (batch, time) or valid.shape != target.shape:
        raise ValueError("Target/mask shape mismatch.")
    if target.dtype != torch.long or valid.dtype != torch.bool:
        raise ValueError("Target must be long and mask Boolean.")
    if smooth_weight < 0 or clip <= 0:
        raise ValueError("Invalid loss weights.")
    if valid.any() and ((target[valid] < 0).any() or (target[valid] >= classes).any()):
        raise ValueError("A valid target is outside the class range.")
    if not valid.any():
        return outputs.sum() * 0.0
    safe_target = target.masked_fill(~valid, -100)
    pairs = valid[:, 1:] & valid[:, :-1]
    losses = []
    for logits in outputs:
        ce = F.cross_entropy(logits, safe_target, reduction="none", weight=class_weight)
        ce = ce[valid].mean()
        log_p = logits.log_softmax(dim=1)
        delta = (log_p[:, :, 1:] - log_p[:, :, :-1]).abs().clamp(max=clip)
        if pairs.any():
            smooth = (delta.square() * pairs[:, None, :]).sum()
            smooth = smooth / (pairs.sum() * classes)
        else:
            smooth = logits.sum() * 0.0
        losses.append(ce + smooth_weight * smooth)
    return torch.stack(losses).mean()


class ChunkPredictor:
    """Eval-only finite history. Context is reset by constructing a new stream.

    Retains the exact receptive field minus one raw feature cells. Missing
    features remain masked but do not reset the learned convolution history.
    """
    def __init__(self, model):
        if model.training:
            raise ValueError("streaming requires eval mode")
        self.model = model
        self.history_x = self.history_valid = None

    @torch.no_grad()
    def push(self, x, valid):
        if self.model.training:
            raise ValueError("streaming requires eval mode")
        if self.history_x is not None:
            joined = torch.cat((self.history_x, x), dim=-1)
            mask = torch.cat((self.history_valid, valid), dim=-1)
        else:
            joined, mask = x, valid
        result = self.model(joined, mask)[..., -x.shape[-1]:]
        keep = self.model.receptive_field - 1
        self.history_x = joined[..., -keep:].detach().clone()
        self.history_valid = mask[..., -keep:].detach().clone()
        return result


class AvailableSequenceStream:
    """Process cells in event order only when their source features are available.

    A delayed earlier feature blocks later cells; this is an explicit ordered
    buffering policy. Caller-provided as_of_us also represents processing time.
    """
    def __init__(self, model, sequence):
        sequence.validate(model.classes)
        self.sequence = sequence
        self.predictor = ChunkPredictor(model)
        self.index = 0
        self.last_as_of = -1

    def advance(self, as_of_us):
        if as_of_us < self.last_as_of:
            raise ValueError("as-of clock must not go backwards")
        self.last_as_of = as_of_us
        out = []
        s = self.sequence
        while self.index < len(s.features) and s.available_us[self.index] <= as_of_us:
            i = self.index
            x = torch.as_tensor(s.features[i:i+1].T.copy(), dtype=torch.float32)[None]
            valid = torch.tensor([[bool(s.valid[i])]])
            logits = self.predictor.push(x, valid)[-1, 0, :, 0]
            out.append({'index': i, 'event_us': int(s.end_us[i]),
                        'available_us': int(as_of_us),
                        'prediction': int(logits.argmax()) if s.valid[i] else None})
            self.index += 1
        return out
