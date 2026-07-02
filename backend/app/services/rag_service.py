from app.llm.base import LLMProvider
from app.schemas.chat import LLMAnswer
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService

class RagService:
	def __init__(
		self,
		embedding_service: EmbeddingService,
		vector_service: VectorService,
		llm_provider: LLMProvider,
	):
		self.embedding_service = embedding_service
		self.vector_service = vector_service
		self.llm_provider = llm_provider

	def ask(
		self,
		video_id: str, 
		question: str,
		trace=None
	) -> LLMAnswer: 
		
		if trace: 
			trace.query = question
			trace.log("QUERY", question)
		
		query_embedding = self.embedding_service.embed_query(question)

		if trace: 
			trace.query_embedding = query_embedding
			trace.log("EMBEDDING", query_embedding[:5])

		chunks, meta = self.vector_service.search(query_embedding, video_id)

		if trace: 
			trace.retrieved_chunks_raw = chunks
			trace.meta = meta 
			trace.log("RAW CHUNKS", chunks)
			trace.log("META", meta)

		response = self.llm_provider.answer(
			question=question,
			chunks=chunks,
			meta=meta,
			trace=trace
		)

		if trace: 
			trace.response = response
			trace.log("FINAL RESPONSE", response)

		return response