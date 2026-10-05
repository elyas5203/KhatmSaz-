import subprocess
import os

tests = {
    "RUN-20261004-002": ("tests/test_join_records_bot_instance.py", "44f5235eebb224a188abdc53fb266eccb1bc65b43a071bf1410e7f15c17f4baa"),
    "RUN-20261004-003": ("tests/test_member_bot_fixes.py::test_next_portion_delivery_records_daily_reminder_to_prevent_duplicate", "c9f4f6e78dfb848348e9fd703f633a127f9751930278c2067226f50be68315a6"),
    "RUN-20261004-004": ("tests/test_migration_graph.py", "091de0d6c6737f700527f45808c57fbcf25b1a0799bdfaf0a0f6ef9742205487"),
    "RUN-20261004-005": ("tests/test_reminder_redesign_p2.py", "b5e9400f2428c65e6be2cbef1ae418e086bda23d6cd80b52e9c13e8f77c4bb1f")
}

head = "a2f55b412078b0ab3b23085c5b2f1cc84c4eb6ce"

for run_id, (target, fhash) in tests.items():
    cmd = [".\\.venv\\Scripts\\python.exe", "-m", "pytest", target, "-q"]
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    env["PYTHONIOENCODING"] = "utf-8"
    
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    
    content = f"""# {run_id} Evidence
- **File**: `{target}`
- **Hash (SHA-256)**: `{fhash}`
- **HEAD**: `{head}`
- **Command**: `{" ".join(cmd)}`
- **Exit Code**: {result.returncode}

## Output
`
{result.stdout}
{result.stderr}
`
"""
    with open(f"c:/xampp/htdocs/Khatm/docs/ai/audit/evidence/{run_id}.md", "w", encoding="utf-8") as f:
        f.write(content)
