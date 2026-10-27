# Lab 5 - Issues Table

**Name:** Samarth Rajesh Rao | **SRN:** PES1UG24AM244 | **Repo:** L5_06_it_helpdesk | **File:** `helpdesk_system.py`

Scores: Pylint **5.53 -> 10.00**, Flake8 **15 -> 0 warnings**, Bandit **1 High + 3 Low -> 0**.
Line numbers refer to the original file.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shell injection via `shell=True` (Bandit B602, High) | Security | 38 | `"ping -c 1 " + hostname` run through a shell; a hostname like `x; rm -rf ~` executes arbitrary commands. `-c` also fails on Windows. | Validate hostname with a regex, call `subprocess.call(["ping", flag, "1", host])` with no shell, choose `-n`/`-c` by platform |
| Hard-coded admin password (Bandit B105) | Security | 8, 55 | `ADMIN_PASSWORD = "helpdesk@123"` and the same literal again in `main()` are committed to source; compared with `==` | Read from `HELPDESK_ADMIN_PASSWORD` env var, compare with `hmac.compare_digest`, deny if unset |
| Bare `except: pass` (Bandit B110, Pylint W0702, Flake8 E722) | Bug / Security | 21-24 | `add_note` swallows every error, so a note for a missing ticket (#999) is silently lost | Explicit `if ticket_id not in tickets` check, report the problem and return `False` |
| Mutable default argument (Pylint W0102) | Bug | 10 | `audit_trail=[]` is shared across all calls, so audit entries leak between unrelated calls | Default `None`, create a new list inside the function |
| Unvalidated urgency (no tool flags it) | Logic bug | 13, 54, 52 | `int(urgency)` accepts `-7` or `99` as priority; non-numeric input (`abc`) crashes the program with a traceback | New `parse_priority()` enforcing 1-5 and raising `ValueError`; `main()` catches it and prints a message |
| Crashes on missing ticket | Logic bug | 17-18, 26-28 | `assign_ticket` raises `KeyError`; `close_ticket` raises `KeyError` for unknown ids; closing silently fails on wrong password | Existence checks; both return `True`/`False` |
| Comparison to None (Flake8 E711, Pylint C0121) | Style | 33 | `== None` | Use `is None` |
| Global statement / constant naming (Pylint W0603, C0103) | Design | 7, 11 | Mutable global `ticket_counter` rebound with `global` | Use `itertools.count(101)` for ids and module-level `TICKETS`, no `global` needed |
| Non-snake_case name (Pylint C0103) | Style | 30 | `unresolvedHighPriority` | Renamed `unresolved_high_priority`, rewritten as a comprehension (also fixes C0206 `.items()`) |
| File opened without `with`/encoding (Pylint R1732, W1514) | Resource | 40-43 | `open()`/`close()` leaks the handle if `write` raises; no encoding | `with open(..., encoding="utf-8")` and `json.dump` |
| PEP 8 layout (Flake8 E302, E305, E501) | Style | 10-58 | Missing blank lines, 3 lines over 79 chars | Reformatted and wrapped |
| Unused variable (Flake8 F841, Pylint W0612) | Style | 47 | `t2` assigned and never used | Call `raise_ticket` without binding |
| Missing docstrings (Pylint C0114/C0116) | Docs | whole file | No module or function docstrings | Added docstrings |
| `%` formatting (Pylint C0209) | Style | 14 | Old-style string formatting | f-strings |
| No `__main__` guard | Design | 58 | `main()` runs on import | `if __name__ == "__main__":` |
| Bandit B404 (import subprocess, Low) | Security | 2 | Informational, flagged on every subprocess import | Kept (needed) after removing the shell use; annotated with `# nosec B404` and `B603/B607` on the safe call |

## Commits
1. `Fix Bandit findings` - B602, B105, B110, B404 (+ baseline "before" reports)
2. `Fix Flake8 findings` - E302, E305, E501, E711, F841 (all Flake8 warnings cleared)
3. `Fix Pylint findings and logic bugs` - docstrings, naming, global, mutable default, `with open`, validation (10.00/10), + "after" reports
