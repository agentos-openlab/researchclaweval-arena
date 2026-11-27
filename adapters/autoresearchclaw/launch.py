"""Configure and invoke the upstream researchclaw pipeline once."""

import json
import os
import sys
from pathlib import Path


workspace = Path(os.environ['WORKSPACE'])
objective = Path('/input/prompt.txt').read_text(encoding='utf-8')
name = os.environ['ARENA_TOPIC']
config = {
    'project': {'name': name, 'mode': 'full-auto'},
    'research': {'topic': name},
    'llm': {
        'provider': 'openai-compatible',
        'base_url': os.environ['OPENAI_BASE_URL'],
        'api_key_env': 'OPENAI_API_KEY',
        'primary_model': os.environ['OPENAI_MODEL'],
        'fallback_models': [],
    },
    'experiment': {
        'mode': 'sandbox',
        'max_iterations': 4,
        'time_budget_sec': 900,
        'metric_direction': 'minimize' if name in {'arc_wbe_2026', 'babylm'} else 'maximize',
        'sandbox': {'python_path': sys.executable},
    },
}
config_path = Path('/tmp/researchclaw-arena.yaml')
# JSON is a subset of YAML and quotes user-provided values correctly.
config_path.write_text(json.dumps(config), encoding='utf-8')
os.execvp('researchclaw', [
    'researchclaw', 'run', '--config', str(config_path), '--topic', objective,
    '--output', str(workspace / 'native-artifacts'), '--auto-approve',
    '--no-graceful-degradation',
])
