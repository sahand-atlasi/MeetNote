from pathlib import Path

from meetnote.application.transcription import FakeTranscriber


def test_fake_transcriber_returns_demo_text() -> None:
    transcriber = FakeTranscriber()

    result = transcriber.transcribe(Path("recording.wav"))

    assert result == (
        "Sahand will review the recording. The team will prepare meeting minutes."
    )
