from openai import OpenAI

from app.llm.base import LLMProvider
from app.llm.prompts import build_video_qa_messages
from app.schemas.chat import Citation, LLMAnswer
from app.schemas.chunk import TranscriptChunk
from app.debug.rag_trace import RAGTrace

class OpenAICompatibleLLM(LLMProvider):
	def __init__(
		self,
		api_key: str,
		model: str, 
		base_url: str | None = None,
	):
		if not api_key: 
			raise ValueError("api_key is required for OpenAICompatibleLLM")
		
		self.model = model 

		if base_url:
			self.client = OpenAI(
				api_key=api_key,
				base_url=base_url
			)
		else: 
			self.client = OpenAI(
				api_key=api_key
			)

	def answer(
		self,
		question: str, 
		chunks: list[TranscriptChunk],
		meta: dict | None = None,
		trace: RAGTrace | None = None
	) -> LLMAnswer:
		if not chunks: 
			return LLMAnswer(
				answer="No relevant transcript context was found for this question.",
				citations=[]
			)
		
		messages = build_video_qa_messages(
			question=question,
			chunks=chunks,
			meta=meta
		)

		if trace: 
			trace.prompt = messages[1]["content"]
			trace.log("PROMPT", messages[1]["content"])

		response = self.client.chat.completions.create(
			model=self.model,
			messages=messages,
			temperature=0.2
		)

		answer_text = response.choices[0].message.content or ""

		citations = [
			Citation(
				start=chunk.start,
				end=chunk.end,
				text=self._shorten(chunk.text, max_chars=500)
			)
			for chunk in chunks[:1] # Temporary 
		]

		return LLMAnswer(
			answer=answer_text.strip(),
			citations=citations
		)
	
	def _shorten(self, text: str, max_chars: int) -> str: 
		clean_text = " ".join(text.split())

		if len(clean_text) <= max_chars:
			return clean_text
		
		return clean_text[:max_chars].rstrip() + "..."