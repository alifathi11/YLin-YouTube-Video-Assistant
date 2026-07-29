from app.config import settings
from app.llm.base import LLMProvider
from app.llm.openai_compatible_llm import OpenAICompatibleLLM
from app.llm.simple_context_llm import SimpleContextLLM


def create_llm_provider() -> LLMProvider:
	provider = settings.llm_provider.lower().strip()

	if provider == "simple":
		return SimpleContextLLM()
	
	if provider in ["openai", "ollama"]:
		if provider == "openai" and not settings.openai_api_key:
			raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
		
		return OpenAICompatibleLLM(
			api_key=settings.openai_api_key or "ollama",
			base_url=settings.openai_base_url,
			model=settings.openai_model
		)
	
	raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")