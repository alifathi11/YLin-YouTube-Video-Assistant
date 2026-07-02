from urllib.parse import urlparse, parse_qs
import yt_dlp
from datetime import datetime

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

def get_youtube_metadata(url: str):
	ydl_opts = {
		"quiet": True,
		"skip_download": True,
		"noplaylist": True,

		"extractor_args": {
			"youtube": {
				"player_client": ["android", "web"]
			}
		},

		"http_headers": {
			"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
		},
	}

	with yt_dlp.YoutubeDL(ydl_opts) as ydl:
		try:
			info = ydl.extract_info(url, download=False)
		except Exception:
			return {
				"title": "",
				"description": "",
				"duration": 0,
				"upload_date": None,
				"channel_name": ""
			}

	return {
		"title": info.get("title"),
		"description": info.get("description"),
		"duration": info.get("duration"),
		"upload_date": info.get("upload_date"),
		"channel_name": info.get("uploader"),
	}