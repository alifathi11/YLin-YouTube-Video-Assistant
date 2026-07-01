from abc import ABC, abstractmethod

from app.schemas.chat import LLMAnswer
from app.schemas.chunk import TranscriptChunk

class LLMProvider(ABC):
	@abstractmethod
	def answer(
		self,
		question: str,
		chunks: list[TranscriptChunk]
	) -> LLMAnswer:
		pass