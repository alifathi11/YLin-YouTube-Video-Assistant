from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.transcript_service import TranscriptService
from app.vector_store.simple_memory_store import SimpleMemoryVectorStore
from app.llm.factory import create_llm_provider
from app.services.rag_service import RagService

transcript_service = TranscriptService()
chunking_service = ChunkingService()
embedding_service = EmbeddingService()
vector_store = SimpleMemoryVectorStore()
llm_provider = create_llm_provider()

rag_service = RagService(
	embedding_service=embedding_service,
	vector_store=vector_store,
	llm_provider=llm_provider,
	top_k=5
)