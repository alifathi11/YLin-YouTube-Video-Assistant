from fastapi import APIRouter, HTTPException

from app.dependencies import (
	chunking_service,
	embedding_service,
	transcript_service,
	vector_store
)

from app.schemas.video import (
	IndexVideoRequest, 
	IndexVideoResponse, 
	PreviewChunksResponse
)

from app.services.chunking_service import ChunkingService
from app.services.transcript_service import TranscriptFetchError, TranscriptService
from app.utils.youtube import extract_video_id

router = APIRouter(prefix="/videos", tags=["videos"])

@router.post("/index", response_model=IndexVideoResponse)
def index_video(request: IndexVideoRequest):
	try: 
		video_id = extract_video_id(request.url)
	except ValueError as exc: 
		raise HTTPException(status_code=400, detail=str(exc))

	try: 
		segments = transcript_service.fetch_transcript(video_id)
	except TranscriptFetchError as exc: 
		raise HTTPException(status_code=404, detail=str(exc))
	
	chunks = chunking_service.create_chunks(
		video_id=video_id,
		segments=segments
	)

	embeddings = embedding_service.embed_passages(
		[chunk.text for chunk in chunks]
	)

	chunks_with_embeddings = []

	for chunk, embedding in zip(chunks, embeddings):
		chunk.embedding = embedding
		chunks_with_embeddings.append(chunk)

	vector_store.add_chunks(chunks_with_embeddings)

	return IndexVideoResponse(
		video_id=video_id,
		status="indexed",
		segments_count=len(segments),
		chunks_count=len(chunks_with_embeddings)
	)
@router.post("/preview-chunks", response_model=PreviewChunksResponse)
def preview_chunks(request: IndexVideoRequest):
	try:
		video_id = extract_video_id(request.url)
	except ValueError as exc: 
		raise HTTPException(status_code=400, detail=str(exc))
	
	try: 
		segments = transcript_service.fetch_transcript(video_id)
	except TranscriptFetchError as exc: 
		raise HTTPException(status_code=404, detail=str(exc))
	
	chunks = chunking_service.create_chunks(
		video_id=video_id,
		segments=segments
	)

	return PreviewChunksResponse(
		video_id=video_id,
		chunks_count=len(chunks),
		chunks=chunks
	)