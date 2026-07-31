import shutil
from pathlib import Path
from typing import Any


class AudioDownloadError(Exception):
    pass


class YoutubeAudioService:
    def __init__(
        self,
        browser_name: str | None = None,
        browser_profile: str | None = None,
        browser_keyring: str | None = None,
        browser_container: str | None = None,
        deno_path: str | None = None,
    ):
        self.browser_name = browser_name
        self.browser_profile = browser_profile
        self.browser_keyring = browser_keyring
        self.browser_container = browser_container
        self.deno_path = deno_path

    def download(
        self,
        video_id: str,
        output_dir: Path,
    ) -> Path:
        try:
            return self._download(video_id, output_dir)
        except Exception as exc:
            raise AudioDownloadError(
                f"Could not download audio for video_id={video_id}"
            ) from exc

    def _download(
        self,
        video_id: str,
        output_dir: Path,
    ) -> Path:
        import yt_dlp

        output_dir.mkdir(parents=True, exist_ok=True)

        deno_path = self.deno_path or shutil.which("deno")

        if deno_path is None:
            raise RuntimeError(
                "Deno was not found. Make sure it is installed and available in PATH."
            )

        video_url = f"https://www.youtube.com/watch?v={video_id}"
        output_template = output_dir / "audio.%(ext)s"

        options: dict[str, Any] = {
            "format": "bestaudio/best",
            "outtmpl": str(output_template),
            "noplaylist": True,
            "overwrites": True,
            "quiet": False,
            "js_runtimes": {
                "deno": {
                    "path": deno_path,
                }
            },
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }
            ],
        }

        if self.browser_name:
            options["cookiesfrombrowser"] = (
                self.browser_name,
                self.browser_profile,
                self.browser_keyring,
                self.browser_container,
            )

        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.download([video_url])

        audio_path = output_dir / "audio.mp3"

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Downloaded audio was not found for video_id={video_id}"
            )

        return audio_path