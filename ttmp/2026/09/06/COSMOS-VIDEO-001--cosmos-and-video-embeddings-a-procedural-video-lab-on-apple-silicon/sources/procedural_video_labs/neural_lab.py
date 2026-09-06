"""A small causal multi-stage TCN and deterministic CPU smoke tests.

Run: python neural_lab.py
Requires PyTorch. This is a teaching variant, not the original MS-TCN.
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
        inputs, outputs = x * mask, []
        for stage in self.stages:
            logits = stage(inputs, mask)
            outputs.append(logits)
            inputs = logits.softmax(dim=1) * mask
        return torch.stack(outputs)  # [stages, batch, classes, time]


def segmentation_loss(outputs: torch.Tensor, target: torch.Tensor,
                      valid: torch.Tensor, smooth_weight: float = 0.05,
                      clip: float = 4.0) -> torch.Tensor:
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
        ce = F.cross_entropy(logits, safe_target, reduction="none")
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


def demo():
    torch.set_num_threads(2)
    torch.manual_seed(7)
    model = CausalMultiStageTCN(8, 3)
    x = torch.randn(2, 8, 24)
    valid = torch.ones(2, 24, dtype=torch.bool)
    model.eval()
    with torch.no_grad():
        full = model(x, valid)
        altered = x.clone()
        altered[:, :, 12:] += 100.0
        changed = model(altered, valid)
        error = (full[:, :, :, :12] - changed[:, :, :, :12]).abs().max().item()
        assert error < 1e-6, "Future input changed a past prediction."
        prefix = model(x[:, :, :12], valid[:, :12])
        assert torch.allclose(full[:, :, :, :12], prefix, atol=1e-6)
    target = torch.arange(24)[None, :].repeat(2, 1) // 8
    # Easy synthetic features for an optimizer smoke test, not a benchmark.
    train_x = F.one_hot(target, 3).float().transpose(1, 2)
    train_x = torch.cat([train_x, torch.zeros(2, 5, 24)], dim=1)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    model.eval()
    initial = float(segmentation_loss(model(train_x, valid), target, valid).detach())
    model.train()
    for _ in range(40):
        optimizer.zero_grad()
        loss = segmentation_loss(model(train_x, valid), target, valid)
        loss.backward()
        optimizer.step()
    model.eval()
    final = float(segmentation_loss(model(train_x, valid), target, valid).detach())
    assert final < initial
    empty_mask = torch.zeros_like(valid)
    empty_loss = segmentation_loss(model(x, valid), target, empty_mask)
    assert empty_loss.item() == 0
    return {
        "output_shape": list(full.shape),
        "future_perturbation_max_prefix_error": error,
        "initial_synthetic_loss": round(initial, 6),
        "final_synthetic_loss": round(final, 6),
        "optimizer_steps": 40,
        "tests": "passed",
        "torch_version": torch.__version__
    }


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2))
