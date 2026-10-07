from pathlib import Path

from meetnote.application.meeting_transcription import MeetingTranscriber
from meetnote.application.transcription import (
    FakeTranscriber,
    TranscriptionService,
)


def test_meeting_transcriber_returns_transcript(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "meeting.wav"
    audio_path.touch()

    transcription_service = TranscriptionService(FakeTranscriber())
    meeting_transcriber = MeetingTranscriber(transcription_service)

    result = meeting_transcriber.transcribe_meeting(audio_path)

    assert result == (
        "Sahand will review the recording. "
        "The team will prepare meeting minutes."
    )