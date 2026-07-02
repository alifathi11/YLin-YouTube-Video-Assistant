from app.schemas.chunk import TranscriptChunk

def build_video_qa_messages(
	question: str, 
	chunks: list[TranscriptChunk],
	meta: dict | None = None
) -> list[dict]:
	
	meta_text = _format_meta(meta)
	context_text = _format_chunks(chunks)

	system_prompt = (
		"You are a YouTube video RAG assistant.\n"
		"Answer using ONLY the provided metadata and transcript chunks.\n"
		"If information is not in them, say it's not available in the video.\n"
		"Do not hallucinate.\n"
	)

	user_prompt = (
		f"{meta_text}\n\n"
		f"TRANSCRIPT CHUNKS:\n{context_text}\n\n"
		f"QUESTION:\n{question}\n"
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

def _format_meta(meta: dict | None) -> str:
    if not meta:
        return "No metadata available."

    return (
        "VIDEO METADATA:\n"
        f"title: {meta.get('title')}\n"
        f"description: {meta.get('description')}\n"
        f"duration: {meta.get('duration')}\n"
        f"upload_date: {meta.get('upload_date')}\n"
        f"channel_name: {meta.get('channel_name')}\n"
    )