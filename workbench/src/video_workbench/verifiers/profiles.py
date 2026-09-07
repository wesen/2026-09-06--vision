"""Small immutable experiment profiles; no inference-library imports."""
import math
from video_workbench.rules.evaluate import digest

CONTRACT_VERSION = 'reasoning-image-v3'
FIELDS = {'id','model_family','prompt_style','system_prompt','temperature','top_p','top_k',
          'repetition_penalty','presence_penalty','penalty_context_size','seed','max_output_tokens','deadline_ms'}


def validate_profile(profile, request=None):
    if not isinstance(profile, dict) or set(profile) != FIELDS:
        raise ValueError('invalid generation profile fields')
    if not isinstance(profile['id'], str) or not profile['id'] or len(profile['id']) > 100:
        raise ValueError('invalid profile id')
    if profile['model_family'] not in ('qwen','cosmos') or profile['prompt_style'] not in ('direct','reasoning'):
        raise ValueError('unsupported profile family/style')
    if profile['system_prompt'] not in ('','You are a helpful assistant.'):
        raise ValueError('unsupported system prompt')
    for key, lo, hi in [('temperature',0,2),('top_p',0.001,1),('repetition_penalty',1,2),('presence_penalty',0,2)]:
        value=profile[key]
        if type(value) not in (int,float) or not math.isfinite(value) or not lo <= value <= hi:
            raise ValueError('invalid profile '+key)
    for key, lo, hi in [('top_k',0,100),('seed',0,2**32-1),('max_output_tokens',1,4096),('deadline_ms',1,120000),('penalty_context_size',1,4096)]:
        value=profile[key]
        if type(value) is not int or not lo <= value <= hi:
            raise ValueError('invalid profile '+key)
    if request is not None and any(profile[k] != request[k] for k in ('max_output_tokens','deadline_ms')):
        raise ValueError('profile/request limits mismatch')
    return profile


def profile_hash(profile):
    return digest(validate_profile(profile))


def make_profile(family, reasoning=False, sampled=False, seed=None):
    if family not in ('qwen','cosmos'):
        raise ValueError('unsupported model family')
    seed = (3407 if family=='qwen' else 1234) if seed is None else seed
    return validate_profile(dict(id=f'{family}-'+('R' if reasoning else 'D')+'-'+('S' if sampled else 'G')+f'-{seed}',
        model_family=family,prompt_style='reasoning' if reasoning else 'direct',
        system_prompt='You are a helpful assistant.' if family=='cosmos' else '',
        temperature=(0.7 if family=='qwen' else 0.6) if sampled else 0.0,
        top_p=(0.8 if family=='qwen' else 0.95) if sampled else 1.0,top_k=20 if sampled else 0,
        repetition_penalty=1.0,presence_penalty=1.5 if sampled and family=='qwen' else 0.0,
        penalty_context_size=4096,seed=seed,max_output_tokens=4096,deadline_ms=120000))


def sampling_kwargs(profile):
    validate_profile(profile)
    return {**{k:profile[k] for k in ('temperature','top_p','top_k','repetition_penalty','presence_penalty')},
            'repetition_context_size':profile['penalty_context_size'],
            'presence_context_size':profile['penalty_context_size']}
