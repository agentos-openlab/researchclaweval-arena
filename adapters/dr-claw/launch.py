"""Apply the terminal compatibility patch and start the native Dr. Claw CLI."""

import os
import subprocess
from pathlib import Path
from urllib.parse import urlsplit


framework = Path('/opt/framework')
workspace = Path(os.environ['WORKSPACE'])
endpoint = urlsplit(os.environ['OPENAI_BASE_URL'])
if endpoint.scheme not in ('http', 'https') or not endpoint.hostname or endpoint.username or endpoint.password:
    raise SystemExit('OPENAI_BASE_URL must be an HTTP(S) API base URL without credentials')
subprocess.run(['git', 'apply', '/arena-adapter/openai-terminal.patch'], cwd=framework, check=True)
# Relative paths work with the terminal CLI's project-scoped file tools.
(workspace / 'arena-input').symlink_to('/input', target_is_directory=True)
(workspace / 'arena-dataset').symlink_to('/dataset', target_is_directory=True)
# The native interactive CLI accepts one logical line. The full task and workflow
# stay in files that it can read with its own tools during that turn.
request = (
    'Run the Arena evaluation described in arena-input/prompt.txt. '
    'Read the full task before choosing the approach. The data is also available '
    'at arena-dataset. Follow the research workflow bundled with Dr. Claw at '
    '/opt/framework/skills/autoresearch/SKILL.md, following the task constraints '
    'on the number of experiments and the required output files. '
    'Complete the research and save the contract outputs in this workspace.\n'
)
args = ['node', str(framework / 'server/cli.js'), 'chat', '--model', os.environ['OPENAI_MODEL']]
raise SystemExit(subprocess.run(args, input=request, text=True, cwd=workspace).returncode)
