from app.schemas.chunk import TranscriptChunk
from app.schemas.transcript import TranscriptSegment

class ChunkingService: 
	def __init__(self, max_words: int = 500, overlap_words: int = 50):
		if max_words <= 0:
			raise ValueError("max_words must be positive")
		
		if overlap_words < 0:
			raise ValueError("overlap_words cannot be negative")
		
		if overlap_words >= max_words:
			raise ValueError("overlap_words must be smaller than max_words")
		
		self.max_words = max_words 
		self.overlap_words = overlap_words

	def create_chunks(
			self,
			video_id: str, 
			segments: list[TranscriptSegment]
	) -> list[TranscriptChunk]:
		chunks: list[TranscriptChunk] = []

		current_segments: list[TranscriptSegment] = []
		current_word_count = 0

		for segment in segments: 
			segment_word_count = self._count_words(segment.text)

			if (
				current_segments
				and current_word_count + segment_word_count > self.max_words
			):
				chunk = self._build_chunk(
					video_id=video_id,
					chunk_index=len(chunks),
					segments=current_segments
				)
				chunks.append(chunk)

				current_segments = self._build_overlap_segments(current_segments)
				current_word_count = sum(
					self._count_words(item.text)
					for item in current_segments
				)

			current_segments.append(segment)
			current_word_count += segment_word_count
	
		if current_segments:
			chunk = self._build_chunk(
				video_id=video_id,
				chunk_index=len(chunks),
				segments=current_segments
			)
			chunks.append(chunk)

		return chunks 
	
	def _build_chunk(
			self,
			video_id: str, 
			chunk_index: int, 
			segments: list[TranscriptSegment]
	) -> TranscriptChunk:
		text = " ".join(segment.text for segment in segments)

		return TranscriptChunk(
			chunk_id=f"{video_id}_{chunk_index:04d}",
			video_id=video_id,
			start=segments[0].start,
			end=segments[-1].end,
			text=text
		)
		
	def _build_overlap_segments(
			self,
			segments: list[TranscriptSegment]
	) -> list[TranscriptSegment]:
		if self.overlap_words == 0:
			return []
	
		overlap_segments: list[TranscriptSegment] = []
		word_count = 0

		for segment in reversed(segments):
			segment_word_count = self._count_words(segment.text)
			
			if word_count + segment_word_count > self.overlap_words:
				break

			overlap_segments.insert(0, segment)
			word_count += segment_word_count

		return overlap_segments
	
	def _count_words(self, text: str) -> int:
		return len(text.split())