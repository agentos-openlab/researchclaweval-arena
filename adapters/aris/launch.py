"""Start the official ARIS-Code research workflow through its native CLI."""

import os
from pathlib import Path


# A user supplies a single OpenAI-compatible service for both ARIS roles.
provider_url = os.environ['OPENAI_BASE_URL']
provider_key = os.environ['OPENAI_API_KEY']
model = os.environ['OPENAI_MODEL']
os.environ.update({
    'EXECUTOR_PROVIDER': 'openai',
    'EXECUTOR_BASE_URL': provider_url,
    'EXECUTOR_API_KEY': provider_key,
    'ARIS_REVIEWER_PROVIDER': 'custom',
    'ARIS_REVIEWER_BASE_URL': provider_url,
    'ARIS_REVIEWER_AUTH_TOKEN': provider_key,
    'ARIS_REVIEWER_MODEL': model,
})
objective = Path('/input/prompt.txt').read_text(encoding='utf-8')
os.execvp('aris', [
    'aris', '--model', model, '--output-format', 'json', '--permission-mode',
    'workspace-write', '--allowedTools', 'Bash(*)', '-p',
    f'/research-pipeline {objective}',
])
