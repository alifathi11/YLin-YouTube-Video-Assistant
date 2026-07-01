import numpy as np 

from app.schemas.chunk import TranscriptChunk
from app.vector_store.base import VectorStore

from app.vector_store.base import VectorStore

class SimpleMemoryVectorStore(VectorStore):
	def __init__(self):
		self.chunks: list[TranscriptChunk] = []

	def add_chunks(self, chunks: list[TranscriptChunk]) -> None:
		if not chunks:
			return 
		
		existing_chunk_ids = {
			chunk.chunk_id
			for chunk in self.chunks
		}

		new_chunks = [
			chunk
			for chunk in chunks 
			if chunk.chunk_id not in existing_chunk_ids
		]

		self.chunks.extend(new_chunks)

	def search(
		self, 
		video_id: str,
		query_embedding: list[float],
		top_k: int = 5
	) -> list[TranscriptChunk]:
		candidates = [
			chunk 
			for chunk in self.chunks
			if chunk.video_id == video_id and chunk.embedding is not None
		]

		if not candidates:
			return []
		
		query_vector = np.array(query_embedding, dtype=np.float32)

		scored_chunks: list[tuple[float, TranscriptChunk]] = []

		for chunk in candidates: 
			chunk_vector = np.array(chunk.embedding, dtype=np.float32)
			score = float(np.dot(query_vector, chunk_vector))

			scored_chunks.append((score, chunk))
		
		scored_chunks.sort(
			key=lambda item: item[0],
			reverse=True
		)
	
		return [
			chunk
			for _, chunk in scored_chunks[:top_k]
		]