from types import SimpleNamespace

class VectorService: 
	def __init__(self, db): 
		self.db = db

	def store_chunk_embedding(self, chunk_id: str, embedding: list[float]):
		self.db.execute(
			"""
			UPDATE chunks 
			SET embedding = %s
			WHERE chunk_id = %s
			""",
			(embedding, chunk_id)
		)

	def search(
		self, 
		query_embedding: list[float], 
		video_id: str, 
		top_k: int = 5
	): 

		query_vec = self._to_vector(query_embedding)

		rows = self.db.fetchall(
			"""
			SELECT chunk_id, video_id, text, start_time, end_time
			FROM chunks 
			WHERE video_id = %s
			ORDER BY embedding <=> %s::vector
			LIMIT %s
			""",
			(video_id, query_vec, top_k)
		)

		return [self._to_chunk(r) for r in rows]
	
	def _to_chunk(self, row):
		return SimpleNamespace(
			chunk_id=row[0],
			video_id=row[1],
			text=row[2],
			start=row[3],
			end=row[4]
		)
	
	def _to_vector(self, vec):
		return "[" + ",".join(map(str, vec)) + "]"
	