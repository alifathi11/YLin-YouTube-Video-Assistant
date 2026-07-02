from app.schemas.chunk import TranscriptChunk

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

		chunk_rows = self.db.fetchall(
			"""
			SELECT chunk_id, video_id, text, start_time, end_time
			FROM chunks 
			WHERE video_id = %s
			ORDER BY embedding <=> %s::vector
			LIMIT %s
			""",
			(video_id, query_vec, top_k)
		)

		chunks = [self._to_chunk(r) for r in chunk_rows]

		video_row = self.db.fetchall(
			"""
			SELECT video_title, video_description, video_duration, video_upload_date, channel_name
			FROM videos
			WHERE video_id = %s
			""", 
			(video_id,)
		)[0]

		meta = self._to_meta(video_row)

		return chunks, meta
	
	def _to_chunk(self, row):
		return TranscriptChunk(
			chunk_id=row[0],
			video_id=row[1],
			text=row[2],
			start=row[3],
			end=row[4]
		)
	
	def _to_meta(self, row): 
		return {
			"title": row[0],
			"description": row[1],
			"duration": row[2],
			"upload_date": row[3],
			"channel_name": row[4]
		}
	
	def _to_vector(self, vec):
		return "[" + ",".join(map(str, vec)) + "]"
	