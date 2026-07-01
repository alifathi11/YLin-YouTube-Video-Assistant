from app.schemas.chunk import TranscriptChunk

def build_video_qa_messages(
	question: str, 
	chunks: list[TranscriptChunk]
) -> list[dict]:
	context_text = _format_chunks(chunks)

	system_prompt = (
		"You are a YouTube video RAG assistant.\n"
		"Answer the user's question using only the provided transcript chunks.\n"
		"Do not use outside knowledge.\n"
		"If the transcript chunks do not contain enough information, say that the video does not contain enough information to answer.\n"
		"Keep the answer clear and concise.\n"
		"Do not invent timestamps.\n"
	)

	user_prompt = (
		f"Question:\n{question}\n\n"
		f"Transcript chunks:\n{context_text}\n\n"
		"Write the answer based only on these chunks."
	)

	return [
		{
			"role": "system",
			"content": system_prompt
		},
		{
			"role": "user",
			"content": user_prompt
		}
	]

def _format_chunks(chunks: list[TranscriptChunk]) -> str: 
	parts: list[str] = []

	for index, chunk in enumerate(chunks, start=1): 
		parts.append(
			"[Chunk {index} | {start} - {end}]\n{text}".format(
				index=index,
				start=_format_time(chunk.start),
				end=_format_time(chunk.end),
				text=chunk.text
			)
		)

	return "\n\n---\n\n".join(parts)

def _format_time(seconds: float) -> str: 
	total_seconds = int(seconds)
	minutes = total_seconds // 60
	remaining_seconds = total_seconds % 60

	return f"{minutes:02d}:{remaining_seconds:02d}"