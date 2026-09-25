# MeetNote

MeetNote is a Python application that helps administrators convert recorded
meetings into reviewable and trackable action items.

The planned workflow is:

1. Upload an audio or video meeting recording.
2. Transcribe the recording locally using Whisper.
3. Extract candidate action items from the transcript.
4. Submit each candidate item for administrative review.
5. Allow the administrator to verify, edit, label, request changes, or reject it.
6. Display verified items on a task board.

## Current status

The project currently includes:

- A Kivy desktop interface.
- An action-item domain model.
- Action-item status-transition rules.
- Automated unit tests.
- Poetry-based dependency management.
- Ruff and mypy static checks.

## Development commands

```powershell
py -3.12 -m poetry install
py -3.12 -m poetry run python -m meetnote
py -3.12 -m poetry run poe test
py -3.12 -m poetry run poe static-checks
py -3.12 -m poetry run poe coverage
```

## Architecture

The project separates:

- User interface code.
- Domain models.
- Application services.
- External adapters.
- Persistence.

## License

This project is distributed under the Apache License 2.0.