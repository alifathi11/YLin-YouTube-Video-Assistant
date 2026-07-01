from fastapi import APIRouter, HTTPException

from app.dependencies import (
	transcript_service,
	chunking_service,
	ingestion_service
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

	segments_count, chunks_count = ingestion_service.ingest(video_id)

	return IndexVideoResponse(
		video_id=video_id,
		status="indexed",
		segments_count=segments_count,
		chunks_count=chunks_count
	)

############################################################################
################################# DEBUG ####################################
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
############################################################################