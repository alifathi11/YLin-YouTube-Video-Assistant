from pydantic import BaseModel

from app.debug.rag_trace import RAGTrace

class AskQuestionRequest(BaseModel):
	video_id: str 
	question: str 
	debug: bool | None = None 

class Citation(BaseModel):
	start: float 
	end: float 
	text: str | None = None 

class AskQuestionResponse(BaseModel):
	answer: str 
	citations: list[Citation]
	trace: RAGTrace | None = None 

class LLMAnswer(BaseModel):
	answer: str
	citations: list[Citation]