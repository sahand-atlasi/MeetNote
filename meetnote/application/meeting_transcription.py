from dataclasses import dataclass
from pathlib import Path

from meetnote.application.transcription import TranscriptionService


@dataclass(frozen=True)
class MeetingTranscript:
    audio_path: Path
    text: str


class MeetingTranscriber:
    def __init__(self, transcription_service: TranscriptionService) -> None:
        self._transcription_service = transcription_service

    def transcribe_meeting(self, audio_path: Path) -> MeetingTranscript:
        text = self._transcription_service.transcribe(audio_path)

        return MeetingTranscript(
            audio_path=audio_path,
            text=text,
        )
