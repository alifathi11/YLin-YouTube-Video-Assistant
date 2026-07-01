from pydantic import BaseModel

class AskQuestionRequest(BaseModel):
	video_id: str 
	question: str 

class Citation(BaseModel):
	start: float 
	end: float 
	text: str | None = None 

class AskQuestionResponse(BaseModel):
	answer: str 
	citations: list[Citation]

class LLMAnswer(BaseModel):
	answer: str
	citations: list[Citation]