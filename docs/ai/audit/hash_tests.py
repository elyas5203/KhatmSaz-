import hashlib
import os

def get_hash(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

files = [
    'tests/test_i18n_coverage.py',
    'tests/test_join_records_bot_instance.py',
    'tests/test_member_bot_fixes.py',
    'tests/test_migration_graph.py',
    'tests/test_reminder_redesign_p2.py'
]

for file in files:
    h = get_hash(file)
    print(f"{file}: {h}")
