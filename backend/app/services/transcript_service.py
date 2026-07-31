from pathlib import Path
from tempfile import TemporaryDirectory

from app.schemas.transcript import TranscriptSegment
from app.services.whisper_service import WhisperService
from app.services.youtube_audio_service import YoutubeAudioService


class TranscriptFetchError(Exception):
    pass


class TranscriptService:
    def __init__(
        self,
        preferred_languages: list[str] | None = None,
        youtube_audio_service: YoutubeAudioService | None = None,
        whisper_service: WhisperService | None = None,
    ):
        self.preferred_languages = preferred_languages or ["en", "fa"]
        self.youtube_audio_service = (
            youtube_audio_service
            or YoutubeAudioService(
                browser_name="chrome",
                browser_keyring="GNOMEKEYRING",
            )
        )
        self.whisper_service = whisper_service or WhisperService()

    def fetch_transcript(self, video_id: str) -> list[TranscriptSegment]:
        try:
            raw_segments = self._fetch_with_youtube_transcript_api(video_id)
        except Exception as transcript_exc:
            try:
                raw_segments = self._fetch_with_whisper(video_id)
            except Exception as whisper_exc:
                raise TranscriptFetchError(
                    "Could not fetch or generate transcript for "
                    f"video_id={video_id}; "
                    f"transcript_error={type(transcript_exc).__name__}; "
                    f"whisper_error={type(whisper_exc).__name__}"
                ) from whisper_exc

        return self._normalize_segments(raw_segments)

    def _fetch_with_youtube_transcript_api(
        self,
        video_id: str,
    ) -> list[dict]:
        from youtube_transcript_api import YouTubeTranscriptApi

        try:
            return YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=self.preferred_languages,
            )
        except AttributeError:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(
                video_id,
                languages=self.preferred_languages,
            )

            return [
                {
                    "text": item.text,
                    "start": item.start,
                    "duration": item.duration,
                }
                for item in transcript
            ]

    def _fetch_with_whisper(self, video_id: str) -> list[dict]:
        with TemporaryDirectory(prefix=f"video_rag_{video_id}_") as temp_dir:
            audio_path = self.youtube_audio_service.download(
                video_id=video_id,
                output_dir=Path(temp_dir),
            )

            return self.whisper_service.transcribe(audio_path)

    def _normalize_segments(
        self,
        raw_segments: list[dict],
    ) -> list[TranscriptSegment]:
        segments: list[TranscriptSegment] = []

        for item in raw_segments:
            start = float(item["start"])
            duration = float(item.get("duration", 0.0))
            end = start + duration
            text = self._clean_text(item.get("text", ""))

            if not text:
                continue

            segments.append(
                TranscriptSegment(
                    start=start,
                    duration=duration,
                    end=end,
                    text=text,
                )
            )

        return segments

    def _clean_text(self, text: str) -> str:
        return " ".join(text.replace("\n", " ").split())