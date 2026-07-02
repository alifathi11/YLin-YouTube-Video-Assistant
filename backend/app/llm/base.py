from abc import ABC, abstractmethod

from app.schemas.chat import LLMAnswer
from app.schemas.chunk import TranscriptChunk
from app.debug.rag_trace import RAGTrace

class LLMProvider(ABC):
	@abstractmethod
	def answer(
		self,
		question: str,
		chunks: list[TranscriptChunk],
		meta: dict | None = None,
		trace: RAGTrace | None = None
	) -> LLMAnswer:
		pass