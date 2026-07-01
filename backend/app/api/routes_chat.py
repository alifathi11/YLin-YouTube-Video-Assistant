from fastapi import APIRouter, HTTPException

from app.dependencies import rag_service
from app.schemas.chat import AskQuestionRequest, AskQuestionResponse, Citation

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/ask", response_model=AskQuestionResponse)
def ask_question(request: AskQuestionRequest):
	result = rag_service.ask(
		video_id=request.video_id,
		question=request.question
	)

	if not result.citations:
		raise HTTPException(
			status_code=404,
			detail="No indexed chunks found for this video_id. Index the video first."
		)
	
	return AskQuestionResponse(
		answer=result.answer,
		citations=result.citations
	)