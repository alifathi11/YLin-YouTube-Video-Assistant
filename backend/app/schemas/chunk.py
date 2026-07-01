from pydantic import BaseModel

class TranscriptChunk(BaseModel):
	chunk_id: str 
	video_id: str 
	start: float 
	end: float 
	text: str
	embedding: list[float] | None = None 