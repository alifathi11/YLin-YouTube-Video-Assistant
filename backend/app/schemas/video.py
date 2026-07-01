from pydantic import BaseModel, Field 
from app.schemas.chunk import TranscriptChunk

class IndexVideoRequest(BaseModel):
	url: str = Field(..., examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"])

class IndexVideoResponse(BaseModel):
	video_id: str
	status: str
	segments_count: int 
	chunks_count: int 

class PreviewChunksResponse(BaseModel):
	video_id: str 
	chunks_count: int 
	chunks: list[TranscriptChunk]