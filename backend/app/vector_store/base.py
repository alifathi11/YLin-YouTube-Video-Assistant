from abc import ABC, abstractmethod 

from app.schemas.chunk import TranscriptChunk

class VectorStore(ABC):
	@abstractmethod
	def add_chunks(self, chunks: list[TranscriptChunk]) -> None: 
		pass 
	
	@abstractmethod
	def search(
		self, 
		video_id: str, 
		query_embedding: list[float], 
		top_k: int = 5
	) -> list[TranscriptChunk]:
		pass 

