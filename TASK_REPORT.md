KHATMSAZ (PY) TASK REPORT
Task            — Fix member bot category attribute access error
Status          — PASS
What I Changed  — The 'khatmsaz_category' attribute injected on member bots is a plain string mapped from the database category column, not a BotCategory enum instance. Removed `.value` to fix the `AttributeError: 'str' object has no attribute 'value'`.
Files Changed   — `src/khatmsaz/bot/handlers/member_start.py`, `src/khatmsaz/bot/handlers/create_khatm.py`
Commands Run    — git add, git commit, git push
Validation      — Pushed to main.
Docs Updated    — None.
Decisions Added — None.
Next Step       — Wait for the user to pull and restart the server.
