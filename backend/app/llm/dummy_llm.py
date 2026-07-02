from app.vector_store.base import LLMProvider 

class DummyLLM(LLMProvider):
	def answer(self, question, chunks, meta, trace):
		return {
			"answer": "This is a temporary answer generated from retrieved chunks.",
			"citation": [
				{
					"start": chunk["start"],
					"end": chunk["end"]
				}
				for chunk in chunks[:2]
			]
		}