import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'container/start.sh'


class EntrypointTests(unittest.TestCase):
    def run_entrypoint(self, variables, arguments=()):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'web').mkdir()
            (root / 'web/index.html').write_text('existing assets')
            (root / 'arozos').write_text(
                '#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n')
            (root / 'arozos').chmod(0o755)
            script = SCRIPT.read_text().replace('cd /arozos', 'cd ' + directory).replace('-C /arozos/', '-C ' + directory + '/')
            env = {'PATH': os.environ['PATH'], **variables}
            result = subprocess.run(['bash', '-c', script, 'start.sh', *arguments],
                                    env=env, text=True, capture_output=True, check=True)
            return json.loads(result.stdout)

    def test_defaults(self):
        self.assertEqual(self.run_entrypoint({}), [])

    def test_values_are_not_split_or_evaluated(self):
        value = 'My Server; $(echo unsafe) *'
        self.assertEqual(self.run_entrypoint({'AROZOS_HOSTNAME': value}),
                         ['-hostname=' + value])

    def test_boolean_false_and_legacy(self):
        self.assertEqual(self.run_entrypoint({'public_reg': 'true',
                                              'AROZOS_PUBLIC_REG': 'false'}),
                         ['-public_reg=false'])
        self.assertEqual(self.run_entrypoint({'hostname': 'Legacy Server'}),
                         ['-hostname=Legacy Server'])

    def test_empty_override_and_cli_precedence(self):
        self.assertEqual(self.run_entrypoint({'hostname': 'legacy',
                                              'AROZOS_HOSTNAME': ''},
                                             ['-hostname=CLI Server']),
                         ['-hostname=', '-hostname=CLI Server'])

    def test_unrelated_environment_is_ignored(self):
        self.assertEqual(self.run_entrypoint({'AROZOS_UNKNOWN': 'value'}), [])
