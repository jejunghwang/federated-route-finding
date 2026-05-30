# AGENTS.md

## Coding conventions
- Python 3.10+ with type hints on public functions.
- Keep modules small and focused; one responsibility per file.
- Use explicit, readable names over clever abstractions.
- Prefer dataclasses and plain dictionaries for config/data flow.

## Simplicity-first rule
- Build the simplest working path for student MVP delivery.
- Avoid overengineering (no unnecessary framework layers).
- Keep local-file workflows as the default path.

## Team workflow rules
- Keep all CLI commands in `README.md` accurate and runnable.
- If scripts or file paths change, update README in the same PR.
- Prefer working, testable code over abstract architecture discussion.

## Testing expectations
- Add/update tests for important utility logic.
- Core config/model/route validation must have lightweight CPU tests.
- Keep tests quick to run for 4-student parallel development.
