from pydantic_settings import BaseSettings, SettingsConfigDict 

class Settings(BaseSettings):
	app_name: str = "YLin | YouTube Video Assistant"
	app_env: str = "development"

	api_prefix: str = "/api"

	llm_provider: str = "simple"

	openai_api_key: str | None = None 
	openai_base_url: str | None = None 
	openai_model: str = "gpt-4o-mini"

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8"
	)

settings = Settings()