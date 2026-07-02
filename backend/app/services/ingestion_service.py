class IngestionService: 
	def __init__(
		self, 
		db, 
		transcript_service, 
		chunking_service, 
		embedding_service,
		vector_service
	): 
		self.db = db
		self.transcript_service = transcript_service 
		self.chunking_service = chunking_service 
		self.embedding_service = embedding_service 
		self.vector_service = vector_service

	def ingest(self, video_id: str, meta: dict): 
		existing = self.db.fetchall(
			"SELECT 1 FROM videos WHERE video_id = %s",
			(video_id,)
		)

		if existing:
			return 0, 0
		
		segments = self.transcript_service.fetch_transcript(video_id)

		self.db.execute(
			"""
			INSERT INTO videos 
			(video_id, video_title, video_description, video_duration, video_upload_date, channel_name) 
			VALUES (%s, %s, %s, %s, %s, %s) 
			ON CONFLICT DO NOTHING
			""",
			(
				video_id, 
				meta["title"], 
				meta["description"], 
				meta["duration"], 
				meta["upload_date"], 
				meta["channel_name"]
			)
		)

		chunks = self.chunking_service.create_chunks(video_id, segments)

		for c in chunks: 
			self.db.execute(
				"""
				INSERT INTO chunks 
				(video_id, chunk_id, start_time, end_time, text)
				VALUES(%s, %s, %s, %s, %s)
				ON CONFLICT (chunk_id) DO NOTHING
				""",
				(video_id, c.chunk_id, c.start, c.end, c.text)
			)

		texts = [c.text for c in chunks]
		embeddings = self.embedding_service.embed_passages(texts)

		for c, e in zip(chunks, embeddings):
			self.vector_service.store_chunk_embedding(c.chunk_id, e)

		return len(segments), len(chunks)