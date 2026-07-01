from app.llm.base import LLMProvider
from app.schemas.chat import LLMAnswer
from app.services.embedding_service import EmbeddingService
from app.vector_store.base import VectorStore
import time

class RagService:
	def __init__(
		self,
		embedding_service: EmbeddingService,
		vector_store: VectorStore,
		llm_provider: LLMProvider,
		top_k: int = 5
	):
		self.embedding_service = embedding_service
		self.vector_store = vector_store
		self.llm_provider = llm_provider
		self.top_k = top_k

	def ask(
		self,
		video_id: str, 
		question: str
	) -> LLMAnswer: 
		query_embedding = self.embedding_service.embed_query(question)

		chunks = self.vector_store.search(
			video_id=video_id,
			query_embedding=query_embedding,
			top_k=self.top_k
		)

		return self.llm_provider.answer(
			question=question,
			chunks=chunks
		)
	
	# def ask(self, video_id: str, question: str):
	# 	t0 = time.perf_counter()

	# 	query_embedding = self.embedding_service.embed_query(question)
	# 	t1 = time.perf_counter()

	# 	chunks = self.vector_store.search(
	# 		video_id=video_id,
	# 		query_embedding=query_embedding,
	# 		top_k=self.top_k
	# 	)
	# 	t2 = time.perf_counter()

	# 	answer = self.llm_provider.answer(
	# 		question=question,
	# 		chunks=chunks
	# 	)
	# 	t3 = time.perf_counter()

	# 	timing_ms = {
	# 		"embedding": (t1 - t0) * 1000,
	# 		"retrieval": (t2 - t1) * 1000,
	# 		"llm": (t3 - t2) * 1000,
	# 	}

	# 	print(timing_ms)

	# 	return self.llm_provider.answer(
	# 		question=query_embedding,
	# 		chunks=chunks
	# 	)