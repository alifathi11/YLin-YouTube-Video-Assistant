CREATE EXTENSION IF NOT EXISTS vector; 

CREATE TABLE IF NOT EXISTS videos (
	id SERIAL PRIMARY KEY,
	video_id TEXT UNIQUE NOT NULL,
	
	video_title TEXT,
	video_description TEXT, 
	video_duration FLOAT,
	video_upload_date TIMESTAMP,

	channel_name TEXT
);

CREATE TABLE IF NOT EXISTS chunks (
	id SERIAL PRIMARY KEY,
	video_id TEXT REFERENCES videos(video_id),

	chunk_id TEXT UNIQUE NOT NULL,

	start_time FLOAT NOT NULL,
	end_time FLOAT NOT NULL,

	text TEXT NOT NULL ,

	embedding VECTOR(384)
);
