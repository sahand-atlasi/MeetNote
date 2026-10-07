from pathlib import Path
from typing import Protocol


class Transcriber(Protocol):
    def transcribe(self, audio_path: Path) -> str:
        ...


class FakeTranscriber:
    def transcribe(self, audio_path: Path) -> str:
        return (
            "Sahand will review the recording. "
            "The team will prepare meeting minutes."
        )


class LocalWhisperTranscriber:
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        try:
            from faster_whisper import WhisperModel  # type: ignore[import-untyped]
        except ImportError as error:
            raise RuntimeError(
                "Local Whisper is not installed. "
                "Install the optional Whisper dependencies first."
            ) from error

        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )

    def transcribe(self, audio_path: Path) -> str:
        segments, _info = self.model.transcribe(
            str(audio_path),
            vad_filter=True,
        )

        return " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        )