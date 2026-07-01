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
		question: str
	) -> LLMAnswer: 
		query_embedding = self.embedding_service.embed_query(question)

		chunks = self.vector_service.search(query_embedding, video_id)

		return self.llm_provider.answer(
			question=question,
			chunks=chunks
		)