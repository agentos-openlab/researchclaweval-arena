"""Pass the Arena contract to EvoScientist's native single-shot mode."""

import json
import os
from pathlib import Path


home = Path(os.environ['HOME'])
config_home = home / '.config'
config_path = config_home / 'evoscientist' / 'config.yaml'
config_path.parent.mkdir(parents=True, exist_ok=True)
config_path.write_text(json.dumps({
    'provider': 'custom-openai',
    'model': os.environ['OPENAI_MODEL'],
    'model_fallbacks': '',
    'use_responses_api': False,
}), encoding='utf-8')
os.environ['XDG_CONFIG_HOME'] = str(config_home)
os.environ['CUSTOM_OPENAI_BASE_URL'] = os.environ['OPENAI_BASE_URL']
os.environ['CUSTOM_OPENAI_API_KEY'] = os.environ['OPENAI_API_KEY']
objective = Path('/input/prompt.txt').read_text(encoding='utf-8')
os.execvp('evosci', [
    'evosci', '--workdir', os.environ['WORKSPACE'], '--auto-mode', '--no-thinking',
    '--output-format', 'stream-json', '-p', objective,
])
