from pydantic import BaseModel

class TranscriptSegment(BaseModel):
	start: float 
	duration: float 
	end: float 
	text: str  