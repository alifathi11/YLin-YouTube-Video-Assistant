from dataclasses import dataclass, field 
from typing import Any 

@dataclass
class RAGTrace: 
	query: str = ""
	query_embedding: Any = None 

	retrieved_chunks_raw: list = field(default_factory=list)
	retrieved_chunks_formatted: list = field(default_factory=list)

	meta: dict = field(default_factory=dict)

	prompt: str = ""
	response: str = ""

	def log(self, title: str, data: Any):
		print(f"\n==={title}===")
		print(data)
