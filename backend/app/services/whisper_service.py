from pathlib import Path
from typing import Any


class WhisperTranscriptionError(Exception):
    pass

class WhisperService:
    def __init__(
        self,
        model_name: str = "tiny",
        language: str | None = None,
        device: str | None = None
    ):
        self.model_name = model_name
        self.language = language
        self.device = device
        self._model = None

    def transcribe(self, audio_path: Path) -> list[dict]: 
        try: 
            return self._transcribe(audio_path)
        except Exception as exc: 
            raise WhisperTranscriptionError(
                f"Could not transcribe audio_path={audio_path}"
            ) from exc
    
    def _transcribe(self, audio_path: Path) -> list[dict]:
        model = self._get_model()

        options: dict[str, Any] = {
            "task": "transcribe",
            "verbose": False,
            "fp16": self._get_device() == "cuda",
        }

        if self.language:
            options["language"] = self.language

        result = model.transcribe(
            str(audio_path),
            **options
        )

        segments: list[dict] = []

        for item in result.get("segments", []):
            start = float(item["start"])
            end = float(item["end"])

            segments.append(
                {
                    "text": item.get("text", ""),
                    "start": start,
                    "duration": end - start,
                }
            )

        return segments

    def _get_model(self):
        if self._model is None: 
            import whisper 

        self._model = whisper.load_model(
            self.model_name,
            device=self._get_device()
        )

        return self._model

    def _get_device(self) -> str: 
        if self.device:
            return self.device 
        
        import torch 

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        return self.device