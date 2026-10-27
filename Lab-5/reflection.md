# Lab 5 - Reflection

**Name:** Samarth Rajesh Rao | **SRN:** PES1UG24AM244

**1. Which issues were the easiest to fix and which were the hardest?**
The easiest were mechanical ones: `== None` to `is None`, blank lines, long lines, an unused variable and missing docstrings. Flake8 states the exact fix and nothing else in the program depends on them. The hardest were the ones that needed a decision about behaviour. Replacing `shell=True` meant validating the hostname and building an argument list, and handling the platform difference for ping flags. Removing the hard-coded password meant deciding where the secret should come from and what happens when it is missing. Removing `global ticket_counter` meant reshaping how ids are generated.

**2. Did the tools report any false positives?**
Mostly no, but a few findings are low value. Bandit B404 only says "you imported subprocess", which is not a bug, and after the shell was removed B603/B607 also fire on a call that is safe because the arguments are a validated list; I suppressed these with targeted `# nosec` comments. B105 flagged a password-looking string, which was a true positive here, though it would be a false positive for any variable that merely has "password" in its name. Pylint's "constant naming" complaint about `ticket_counter` was a style opinion rather than a defect. Also, the tools missed real bugs: priority `-7` was accepted, non-numeric input crashed the program, and unknown ticket ids raised `KeyError`. I found those by running the program.

**3. How would you integrate static analysis into a real workflow?**
Run flake8, pylint and bandit locally via pre-commit hooks so problems are caught before a commit, and again in CI (e.g. GitHub Actions) on every pull request, failing the build on any Bandit finding, any Flake8 warning, or a Pylint score under a threshold such as 9.5. Keep configuration (`.flake8`, `.pylintrc`, `pyproject.toml`) in the repo so everyone gets the same rules, and require justification for every `# nosec` or `# pylint: disable`.

**4. What tangible improvements did you see in the code?**
Pylint went from 5.53 to 10.00/10, Flake8 from 15 warnings to 0 and Bandit from 1 High and 3 Low issues to 0. More importantly the behaviour is safer and more robust: no command injection, no secret in source, invalid urgency and missing tickets are reported instead of crashing or being silently ignored, the audit trail no longer leaks between calls, and the file handle is always closed. The code is also easier to read and import because of docstrings, snake_case names and the `__main__` guard.
