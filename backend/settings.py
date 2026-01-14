"""Application settings for SaltShark"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Custom settings for SaltShark"""
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")
    
    # Project info
    project_name: str = Field(default="SaltShark API")
    version: str = Field(default="0.1.0")
    description: str = Field(default="Web UI API for SaltStack/SaltProject")
    debug: bool = Field(default=True)
    
    # Server settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    
    # CORS settings
    cors_allow_origins: list[str] = Field(default=["*"])
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: list[str] = Field(default=["*"])
    cors_allow_headers: list[str] = Field(default=["*"])
    
    # Salt API settings
    salt_api_url: str = Field(default="http://localhost:8000")
    salt_api_user: str = Field(default="saltapi")
    salt_api_password: str = Field(default="saltapi")
    
    # JWT settings  
    secret_key: str = Field(default="your-secret-key-here-change-in-production")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    # Database
    database_url: str = Field(default="sqlite://./saltshark.db")
    
    # Middleware
    enable_gzip: bool = Field(default=True)
    enable_trusted_host: bool = Field(default=False)
    
    # Route validation
    validate_routes: bool = Field(default=True)
    
    # Backward compatibility properties (uppercase versions)
    @property
    def SALT_API_URL(self) -> str:
        """Backward compatibility for uppercase SALT_API_URL"""
        return self.salt_api_url
    
    @property
    def SALT_API_USER(self) -> str:
        """Backward compatibility for uppercase SALT_API_USER"""
        return self.salt_api_user
    
    @property
    def SALT_API_PASSWORD(self) -> str:
        """Backward compatibility for uppercase SALT_API_PASSWORD"""
        return self.salt_api_password
    
    @property
    def CORS_ORIGINS(self) -> list[str]:
        """Backward compatibility for uppercase CORS_ORIGINS"""
        return self.cors_allow_origins
    
    @property
    def SECRET_KEY(self) -> str:
        """Backward compatibility for uppercase SECRET_KEY"""
        return self.secret_key
    
    @property
    def ALGORITHM(self) -> str:
        """Backward compatibility for uppercase ALGORITHM"""
        return self.jwt_algorithm
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        """Backward compatibility for uppercase ACCESS_TOKEN_EXPIRE_MINUTES"""
        return self.access_token_expire_minutes


# Create settings instance
settings = Settings()
