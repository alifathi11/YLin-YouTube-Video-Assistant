from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.transcript_service import TranscriptService
from app.services.vector_service import VectorService
from app.services.rag_service import RagService
from app.services.ingestion_service import IngestionService
from app.llm.factory import create_llm_provider
from app.db.postgres import PostgresDB
from app.db.init_db import DBInitializer

transcript_service = TranscriptService()
chunking_service = ChunkingService()
embedding_service = EmbeddingService()

db = PostgresDB(
	dsn="postgresql://postgres:postgres@localhost:5433/ylin"
)
db_initializer = DBInitializer(db)
vector_service = VectorService(db)

llm_provider = create_llm_provider()

ingestion_service = IngestionService(
	db,
	transcript_service=transcript_service,
	chunking_service=chunking_service,
	embedding_service=embedding_service,
	vector_service=vector_service
)

rag_service = RagService(
	embedding_service=embedding_service,
	vector_service=vector_service,
	llm_provider=llm_provider
)