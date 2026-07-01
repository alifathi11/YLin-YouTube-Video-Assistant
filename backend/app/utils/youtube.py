from urllib.parse import urlparse, parse_qs

def extract_video_id(url: str) -> str: 
	parsed = urlparse(url)

	if parsed.hostname in {"www.youtube.com", "youtube.com", "m.youtube.com"}:
		query = parse_qs(parsed.query)
		video_ids = query.get("v")

		if video_ids: 
			return video_ids[0]
		
	if parsed.hostname == "youtu.be":
		video_id = parsed.path.strip("/")

		if video_id:
			return video_id
		
	raise ValueError("Invalid Youtube URL")