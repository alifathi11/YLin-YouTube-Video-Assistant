from sentence_transformers import SentenceTransformer

class EmbeddingService: 
	def __init__(self, model_name: str = "intfloat/multilingual-e5-small"):
		self.model_name = model_name 
		self.model = SentenceTransformer(model_name)

	def embed_query(self, query: str) -> list[float]: 
		text = f"query: {query}"

		embedding = self.model.encode(
			text, 
			normalize_embeddings=True
		)

		return embedding.tolist()
	
	def embed_passage(self, text: str) -> list[float]:
		text = f"passage: {text}"

		embedding = self.model.encode( 
			text,
			normalize_embeddings=True
		)

		return embedding.tolist()
	
	def embed_passages(self, texts: list[str]) -> list[list[float]]:
		if not texts: 
			return []
		
		prefixed_texts = [
			f"passage: {text}"
			for text in texts
		]

		embeddings = self.model.encode(
			prefixed_texts,
			normalize_embeddings=True
		)

		return embeddings.tolist()