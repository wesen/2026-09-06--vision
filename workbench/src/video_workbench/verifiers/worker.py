"""Isolated image worker. The host binds answer identities."""
from pathlib import Path
import argparse
import importlib.metadata
import json
import time
from .adapter import check_packet
from .visibility import prompt, experiment_prompt
from .profiles import validate_profile, profile_hash, sampling_kwargs, CONTRACT_VERSION


def run(model_path, request_path, result_path, variant, profile_path=None, *, prompt_override=None):
    request = json.loads(Path(request_path).read_text())
    check_packet(request)
    profile = json.loads(Path(profile_path).read_text()) if profile_path else None
    if profile is not None:
        validate_profile(profile, request)
    import mlx.core as mx
    from mlx_vlm import load, generate
    from mlx_vlm.utils import load_config, prepare_inputs, should_add_special_tokens
    from mlx_vlm.prompt_utils import apply_chat_template
    started = time.monotonic()
    model, processor = load(model_path, trust_remote_code=False)
    loaded = time.monotonic()
    text = experiment_prompt(request, profile) if profile is not None else prompt(request, variant)
    if prompt_override is not None:
        if not isinstance(prompt_override, str) or not prompt_override.strip() or len(prompt_override)>16000:
            raise ValueError('invalid prompt override')
        text = prompt_override
    config = load_config(model_path)
    formatted = apply_chat_template(processor, config, text, num_images=1)
    if profile is not None and profile['system_prompt']:
        messages = apply_chat_template(processor, config, text, num_images=1, return_messages=True)
        messages.insert(0, {'role': 'system', 'content': profile['system_prompt']})
        formatted = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    kwargs = dict(temperature=0.0)
    processed = None
    if profile is not None:
        import inspect
        from mlx_vlm.generate.ar import generate_step
        kwargs = sampling_kwargs(profile)
        if not set(kwargs) <= set(inspect.signature(generate_step).parameters):
            raise ValueError('installed runtime cannot apply requested sampling profile')
        inputs = prepare_inputs(processor, images=[request['frames'][0]['path']], prompts=formatted,
            image_token_index=getattr(model.config, 'image_token_index', None),
            add_special_tokens=should_add_special_tokens(model.config.model_type, processor))
        processed = {k: {'shape': list(v.shape), 'dtype': str(v.dtype)}
                     for k, v in inputs.items() if hasattr(v, 'shape')}
        grid = inputs.get('image_grid_thw')
        if grid is not None:
            processed['image_grid_thw']['values'] = grid.tolist()
            patch = getattr(processor.image_processor, 'patch_size', 16)
            processed['resized_images_hw'] = [[int(h)*patch, int(w)*patch] for _,h,w in grid.tolist()]
        kwargs.update({k:v for k,v in inputs.items() if k != 'attention_mask'})
        kwargs['mask'] = inputs.get('attention_mask')
        mx.random.seed(profile['seed'])
    generation_started = time.monotonic()
    generated = generate(model, processor, formatted, image=[request['frames'][0]['path']],
        max_tokens=request['max_output_tokens'], verbose=False, **kwargs)
    record = dict(request_id=request['request_id'], raw=generated.text, prompt=text, formatted_prompt=formatted,
        mode='single_image', load_seconds=loaded-started, preparation_seconds=generation_started-loaded,
        generation_seconds=time.monotonic()-generation_started, peak_mlx_bytes=mx.get_peak_memory(),
        prompt_tokens=generated.prompt_tokens, generation_tokens=generated.generation_tokens,
        finish_reason=generated.finish_reason,
        versions={name:importlib.metadata.version(name) for name in ('mlx','mlx-vlm','transformers')})
    if profile is not None:
        record.update(profile=profile, profile_sha256=profile_hash(profile), schema_version=CONTRACT_VERSION,
            processed_inputs=processed, resolved_sampling=sampling_kwargs(profile),
            penalty_scope='MLX recent 4096 input/generated tokens; local approximation, not vLLM parity')
    Path(result_path).write_text(json.dumps(record, indent=2)+'\n')


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('model');p.add_argument('request');p.add_argument('result');p.add_argument('variant')
    p.add_argument('--profile')
    a=p.parse_args();run(a.model,a.request,a.result,a.variant,a.profile)
