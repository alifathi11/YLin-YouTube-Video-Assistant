from app.llm.base import LLMProvider
from app.schemas.chat import Citation, LLMAnswer
from app.schemas.chunk import TranscriptChunk

class SimpleContextLLM(LLMProvider):
	def answer(
		self, 
		question: str,
		chunks: list[TranscriptChunk]
	) -> LLMAnswer:
		if not chunks:
			return LLMAnswer(
				answer="No relevant transcript context was found for this question.",
				citations=[]
			)
		
		best_chunk = chunks[0]

		answer = (
			"Based on the retrieved transcript context, the most relevant part "
			"appears to be around "
			f"{self._format_time(best_chunk.start)} - {self._format_time(best_chunk.end)}.\n\n"
			f"Relevant transcript excerpt:\n{self._shorten(best_chunk.text, max_chars=700)}"
		)

		citations = [
			Citation(
				start=chunk.start,
				end=chunk.end,
				text=self._shorten(chunk.text, max_chars=500)
			)
			for chunk in chunks[:3]
		]

		return LLMAnswer(
			answer=answer,
			citations=citations
		)
	
	def _shorten(self, text: str, max_chars: int) -> str: 
		clean_text = " ".join(text.split())
		
		if len(clean_text) <= max_chars:
			return clean_text
		
		return clean_text[:max_chars].rstrip() + "..."
	
	def _format_time(self, seconds: float) -> str:
		total_seconds = int(seconds)
		minutes = total_seconds // 60
		remaining_seconds =  total_seconds % 60

		return f"{minutes:02d}:{remaining_seconds:02d}"