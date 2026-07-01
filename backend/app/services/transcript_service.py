from app.schemas.transcript import TranscriptSegment

class TranscriptFetchError(Exception):
	pass 

class TranscriptService: 
	def __init__(self, preferred_languages: list[str] | None = None):
		self.preferred_languages = preferred_languages or ["en", "fa"]

	def fetch_transcript(self, video_id: str) -> list[TranscriptSegment]:
		try:
			raw_segments = self._fetch_with_youtube_transcript_api(video_id)
		except Exception as exc:
			raise TranscriptFetchError(
				f"Could not fetch transcript for video_id={video_id}"
			) from exc
		
		return self._normalize_segments(raw_segments)
	
	def _fetch_with_youtube_transcript_api(self, video_id: str) -> list[dict]:
		
		from youtube_transcript_api import YouTubeTranscriptApi

		try:
			return YouTubeTranscriptApi.get_transcript(
				video_id, 
				languages=self.preferred_languages
			)
		except AttributeError: 
			api = YouTubeTranscriptApi()
			transcript = api.fetch(
				video_id,
				languages=self.preferred_languages
			)

			return [
				{
					"text": item.text,
					"start": item.start, 
					"duration": item.duration,
				}
				for item in transcript
			]
	
	def _normalize_segments(self, raw_segments: list[dict]) -> list[TranscriptSegment]:
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
					text=text
				)
			)

		return segments
	
	def _clean_text(self, text: str) -> str: 
		return " ".join(text.replace("\n", " ").split())