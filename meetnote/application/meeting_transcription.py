from pathlib import Path

from meetnote.application.transcription import TranscriptionService


class MeetingTranscriber:
    def __init__(self, transcription_service: TranscriptionService) -> None:
        self._transcription_service = transcription_service

    def transcribe_meeting(self, audio_path: Path) -> str:
        return self._transcription_service.transcribe(audio_path)