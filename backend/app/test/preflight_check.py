from __future__ import annotations

import logging
import os
import shutil
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal


# =============================================================================
# configuration
# =============================================================================

# General
REQUEST_TIMEOUT_SECONDS = 15
STRICT_MODE = False
CLEANUP_TEMP_FILES = True

# The script searches upward for a directory containing app/config.py.
PROJECT_ROOT_OVERRIDE: str | None = None

# Local addresses must bypass system proxies, especially when Ollama is local.
LOCAL_NO_PROXY_HOSTS = ["localhost", "127.0.0.1", "127.0.0.0/8", "::1"]

# Database
# This matches the DSN currently used in app/dependencies.py.
DATABASE_DSN = "postgresql://postgres:postgres@localhost:5433/ylin"

# YouTube connectivity
YOUTUBE_CONNECTIVITY_URL = "https://www.youtube.com/generate_204"

# yt-dlp sample
# This check uses app.services.youtube_audio_service.YoutubeAudioService.
YTDLP_SAMPLE_VIDEO_ID = "jNQXAC9IVRw"
YTDLP_BROWSER_NAME: str | None = "chrome"
YTDLP_BROWSER_PROFILE: str | None = None
YTDLP_BROWSER_KEYRING: str | None = "GNOMEKEYRING"
YTDLP_BROWSER_CONTAINER: str | None = None

# Keep this as None to reproduce the project's current behavior, which searches
# for Deno in PATH. Set an absolute path if needed, for example:
# "/home/ali/.deno/bin/deno"
YTDLP_DENO_PATH: str | None = None

# Whisper sample
# This check uses app.services.whisper_service.WhisperService, which currently
# uses the openai-whisper package imported as `whisper`.
WHISPER_MODEL_NAME = "tiny"
WHISPER_LANGUAGE: str | None = None
WHISPER_DEVICE: str | None = "cpu"

# Optional existing audio file. When None, the audio downloaded by the yt-dlp
# check is used.
WHISPER_SAMPLE_AUDIO_PATH: str | None = None

# youtube-transcript-api sample
# This check calls the exact implementation inside TranscriptService.
TRANSCRIPT_SAMPLE_VIDEO_ID = "dQw4w9WgXcQ"
TRANSCRIPT_LANGUAGES = ["en", "fa"]

# LLM
# The provider, model, API key, and base URL are read from the project's .env
# through app.config.settings and app.llm.factory.create_llm_provider().
LLM_TEST_QUESTION = "What is the test transcript about?"
LLM_TEST_CHUNK_TEXT = (
    "This is a preflight test transcript. Its purpose is to verify that the "
    "configured LLM provider can receive context and return an answer."
)
LLM_TEST_META = {
    "title": "Preflight test video",
    "description": "Synthetic metadata used only for the LLM connectivity test.",
    "duration": 10,
    "upload_date": "20260731",
    "channel_name": "Preflight",
}


# =============================================================================
# Project path and environment preparation
# =============================================================================


def _find_project_root() -> Path:
    if PROJECT_ROOT_OVERRIDE:
        root = Path(PROJECT_ROOT_OVERRIDE).expanduser().resolve()
        if not (root / "app" / "config.py").is_file():
            raise RuntimeError(
                "PROJECT_ROOT_OVERRIDE does not contain app/config.py: "
                f"{root}"
            )
        return root

    script_path = Path(__file__).resolve()

    for parent in script_path.parents:
        if (parent / "app" / "config.py").is_file():
            return parent

    raise RuntimeError(
        "Could not find the project root. Set PROJECT_ROOT_OVERRIDE at the "
        "top of this file."
    )


def _merge_no_proxy_hosts() -> None:
    existing_values: list[str] = []

    for variable_name in ("NO_PROXY", "no_proxy"):
        raw_value = os.environ.get(variable_name, "")
        existing_values.extend(
            item.strip() for item in raw_value.split(",") if item.strip()
        )

    merged_hosts = list(dict.fromkeys(existing_values + LOCAL_NO_PROXY_HOSTS))
    merged_value = ",".join(merged_hosts)
    os.environ["NO_PROXY"] = merged_value
    os.environ["no_proxy"] = merged_value


PROJECT_ROOT = _find_project_root()
TEMP_DIRECTORY = PROJECT_ROOT / ".preflight_tmp"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# app.config uses env_file=".env", so imports must happen with the backend root
# as the current working directory to load the same .env as the main program.
os.chdir(PROJECT_ROOT)
_merge_no_proxy_hosts()


# =============================================================================
# Result model and logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)
LOGGER = logging.getLogger("preflight")

Status = Literal["PASS", "WARNING"]


@dataclass(slots=True)
class CheckResult:
    name: str
    status: Status
    detail: str
    duration_seconds: float

    @property
    def success(self) -> bool:
        return self.status == "PASS"


@dataclass(slots=True)
class RuntimeState:
    downloaded_audio_path: Path | None = None


STATE = RuntimeState()


def _format_exception(exc: Exception) -> str:
    messages: list[str] = []
    current: BaseException | None = exc

    while current is not None:
        message = str(current).strip() or "no details"
        formatted = f"{type(current).__name__}: {message}"

        if formatted not in messages:
            messages.append(formatted)

        current = current.__cause__

    return " <- ".join(messages)


def _run_check(name: str, function: Callable[[], str]) -> CheckResult:
    started_at = time.perf_counter()

    try:
        detail = function()
        duration = time.perf_counter() - started_at
        LOGGER.info("PASS    | %s | %s", name, detail)
        return CheckResult(name, "PASS", detail, duration)
    except Exception as exc:
        duration = time.perf_counter() - started_at
        detail = _format_exception(exc)
        LOGGER.warning("WARNING | %s | %s", name, detail)
        return CheckResult(name, "WARNING", detail, duration)


# =============================================================================
# Individual checks using the project's actual classes
# =============================================================================


def check_database_connection() -> str:
    from app.db.postgres import PostgresDB

    db = PostgresDB(DATABASE_DSN)

    try:
        rows = db.fetchall("SELECT 1")

        if rows != [(1,)]:
            raise RuntimeError(f"Unexpected database response: {rows!r}")
    finally:
        db.conn.close()

    return (
        "PostgresDB connected successfully, pgvector registration completed, "
        "and SELECT 1 returned correctly"
    )


def check_youtube_connection() -> str:
    request = urllib.request.Request(
        YOUTUBE_CONNECTIVITY_URL,
        headers={"User-Agent": "Mozilla/5.0 preflight-check"},
        method="GET",
    )

    with urllib.request.urlopen(
        request,
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as response:
        status = response.getcode()

    if status >= 400:
        raise RuntimeError(f"YouTube returned HTTP {status}")

    return f"YouTube is reachable with HTTP {status}"


def check_ytdlp_sample() -> str:
    from app.services.youtube_audio_service import YoutubeAudioService

    TEMP_DIRECTORY.mkdir(parents=True, exist_ok=True)

    service = YoutubeAudioService(
        browser_name=YTDLP_BROWSER_NAME,
        browser_profile=YTDLP_BROWSER_PROFILE,
        browser_keyring=YTDLP_BROWSER_KEYRING,
        browser_container=YTDLP_BROWSER_CONTAINER,
        deno_path=(
            str(Path(YTDLP_DENO_PATH).expanduser().resolve())
            if YTDLP_DENO_PATH
            else None
        ),
    )

    audio_path = service.download(
        video_id=YTDLP_SAMPLE_VIDEO_ID,
        output_dir=TEMP_DIRECTORY,
    )

    if not audio_path.is_file():
        raise RuntimeError(f"YoutubeAudioService returned a missing file: {audio_path}")

    if audio_path.stat().st_size <= 0:
        raise RuntimeError(f"Downloaded audio is empty: {audio_path}")

    STATE.downloaded_audio_path = audio_path

    return (
        "YoutubeAudioService downloaded audio through yt-dlp: "
        f"{audio_path.name} ({audio_path.stat().st_size} bytes)"
    )


def _resolve_whisper_audio_path() -> Path:
    if WHISPER_SAMPLE_AUDIO_PATH:
        audio_path = Path(WHISPER_SAMPLE_AUDIO_PATH).expanduser().resolve()
    elif STATE.downloaded_audio_path:
        audio_path = STATE.downloaded_audio_path
    else:
        raise RuntimeError(
            "No audio is available for Whisper. The yt-dlp check failed and "
            "WHISPER_SAMPLE_AUDIO_PATH is not set."
        )

    if not audio_path.is_file():
        raise RuntimeError(f"Whisper sample audio does not exist: {audio_path}")

    return audio_path


def check_whisper_sample() -> str:
    from app.services.whisper_service import WhisperService

    audio_path = _resolve_whisper_audio_path()
    service = WhisperService(
        model_name=WHISPER_MODEL_NAME,
        language=WHISPER_LANGUAGE,
        device=WHISPER_DEVICE,
    )

    segments = service.transcribe(audio_path)

    texts = [
        str(segment.get("text", "")).strip()
        for segment in segments
        if str(segment.get("text", "")).strip()
    ]

    if not texts:
        raise RuntimeError("WhisperService returned no transcript text")

    preview = " ".join(texts)[:140]
    return (
        f"WhisperService using model={WHISPER_MODEL_NAME!r}, "
        f"device={service._get_device()!r} returned {len(segments)} segments; "
        f"preview={preview!r}"
    )


def check_youtube_transcript_api_sample() -> str:
    from app.services.transcript_service import TranscriptService

    service = TranscriptService(preferred_languages=TRANSCRIPT_LANGUAGES)

    # This intentionally calls the same internal implementation used by
    # TranscriptService, while isolating youtube-transcript-api from Whisper
    # fallback behavior.
    raw_segments = service._fetch_with_youtube_transcript_api(
        TRANSCRIPT_SAMPLE_VIDEO_ID
    )
    segments = service._normalize_segments(raw_segments)

    if not segments:
        raise RuntimeError(
            "TranscriptService received no usable segments from "
            "youtube-transcript-api"
        )

    preview = " ".join(segment.text for segment in segments)[:140]
    return (
        "TranscriptService successfully used youtube-transcript-api and "
        f"normalized {len(segments)} segments; preview={preview!r}"
    )


def check_llm_provider() -> str:
    from app.config import settings
    from app.llm.factory import create_llm_provider
    from app.schemas.chunk import TranscriptChunk

    provider = create_llm_provider()
    chunk = TranscriptChunk(
        chunk_id="preflight_0000",
        video_id="preflight",
        start=0.0,
        end=10.0,
        text=LLM_TEST_CHUNK_TEXT,
    )

    # This call mirrors RagService.ask(), including meta and trace arguments.
    answer = provider.answer(
        question=LLM_TEST_QUESTION,
        chunks=[chunk],
        meta=LLM_TEST_META,
        trace=None,
    )

    answer_text = str(answer.answer).strip()

    if not answer_text:
        raise RuntimeError("The configured LLM provider returned an empty answer")

    provider_name = type(provider).__name__
    base_url = settings.openai_base_url or "OpenAI default"

    return (
        f"create_llm_provider selected {provider_name} "
        f"(LLM_PROVIDER={settings.llm_provider!r}, "
        f"model={settings.openai_model!r}, base_url={base_url!r}); "
        f"reply={answer_text[:140]!r}"
    )


# =============================================================================
# Runner
# =============================================================================


def _print_summary(results: list[CheckResult]) -> None:
    passed = sum(result.success for result in results)
    warnings = len(results) - passed

    print("\n" + "=" * 100)
    print("PROJECT PREFLIGHT CHECK SUMMARY")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")

    for result in results:
        print(
            f"{result.status:<7} | {result.name:<34} | "
            f"{result.duration_seconds:>7.2f}s | {result.detail}"
        )

    print("-" * 100)
    print(f"Passed: {passed} | Warnings: {warnings} | Total: {len(results)}")
    print("=" * 100)


def main() -> int:
    TEMP_DIRECTORY.mkdir(parents=True, exist_ok=True)

    checks: list[tuple[str, Callable[[], str]]] = [
        ("Database connection", check_database_connection),
        ("YouTube connection", check_youtube_connection),
        ("Project yt-dlp service", check_ytdlp_sample),
        ("Project Whisper service", check_whisper_sample),
        ("Project transcript API service", check_youtube_transcript_api_sample),
        ("Project LLM provider", check_llm_provider),
    ]

    try:
        results = [_run_check(name, function) for name, function in checks]
        _print_summary(results)
    finally:
        if CLEANUP_TEMP_FILES:
            shutil.rmtree(TEMP_DIRECTORY, ignore_errors=True)

    has_warning = any(not result.success for result in results)

    if STRICT_MODE and has_warning:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
