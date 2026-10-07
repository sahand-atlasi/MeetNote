from pathlib import Path

from meetnote.application.meeting_transcription import (
    MeetingTranscript,
    MeetingTranscriber,
)
from meetnote.application.services import MeetingService
from meetnote.application.transcription import (
    FakeTranscriber,
    TranscriptionService,
)


def test_meeting_transcriber_returns_structured_transcript(
    tmp_path: Path,
) -> None:
    audio_path = tmp_path / "meeting.wav"
    audio_path.touch()

    transcription_service = TranscriptionService(FakeTranscriber())
    meeting_transcriber = MeetingTranscriber(transcription_service)

    result = meeting_transcriber.transcribe_meeting(audio_path)

    assert isinstance(result, MeetingTranscript)
    assert result.audio_path == audio_path
    assert result.text == (
        "Sahand will review the recording. The team will prepare meeting minutes."
    )


def test_meeting_service_saves_transcript_to_database(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "meetnote.db"
    audio_path = tmp_path / "meeting.wav"
    audio_path.touch()

    service = MeetingService(database_path)
    meeting_id = service.create_meeting("Weekly meeting")

    result = service.transcribe_meeting(meeting_id, audio_path)

    assert result == (
        "Sahand will review the recording. The team will prepare meeting minutes."
    )

    meeting = service.meetings.get(meeting_id)

    assert meeting is not None
    assert meeting.notes == ""
