"""
Nexus Commander - Configuration Module
Central configuration for all platform services
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class GridAPIConfig:
    """GRID Data API Configuration"""
    base_url: str = "https://api.grid.gg/central-data/graphql"
    api_key: Optional[str] = os.getenv("GRID_API_KEY")
    timeout: int = 30


@dataclass
class PulsarConfig:
    """Apache Pulsar Configuration"""
    service_url: str = os.getenv("PULSAR_URL", "pulsar://localhost:6650")
    topic_prefix: str = "persistent://nexus/esports"
    subscription_name: str = "nexus-commander"


@dataclass
class BigQueryConfig:
    """Google BigQuery Configuration"""
    project_id: str = os.getenv("GCP_PROJECT_ID", "nexus-commander")
    dataset_id: str = "esports_telemetry"
    credentials_path: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


@dataclass
class PineconeConfig:
    """Pinecone Vector Database Configuration"""
    api_key: Optional[str] = os.getenv("PINECONE_API_KEY")
    environment: str = os.getenv("PINECONE_ENV", "us-west1-gcp")
    index_name: str = "nexus-match-embeddings"
    dimension: int = 1536  # OpenAI ada-002 / sentence-transformers dimension


@dataclass
class LLMConfig:
    """LLM Configuration for Claude and Gemini"""
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    claude_model: str = "claude-3-5-sonnet-20241022"
    gemini_model: str = "gemini-1.5-pro"
    max_tokens: int = 8192
    temperature: float = 0.7


@dataclass
class AWSConfig:
    """AWS Services Configuration"""
    region: str = os.getenv("AWS_REGION", "us-east-1")
    access_key: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    step_functions_arn: Optional[str] = os.getenv("STEP_FUNCTIONS_ARN")
    bedrock_model: str = "anthropic.claude-3-sonnet-20240229-v1:0"


@dataclass
class FirebaseConfig:
    """Firebase Configuration"""
    credentials_path: Optional[str] = os.getenv("FIREBASE_CREDENTIALS")
    database_url: str = os.getenv("FIREBASE_DB_URL", "https://nexus-commander.firebaseio.com")


@dataclass
class MLConfig:
    """Machine Learning Models Configuration"""
    # XGBoost parameters
    xgb_n_estimators: int = 500
    xgb_max_depth: int = 8
    xgb_learning_rate: float = 0.05
    
    # TFT parameters
    tft_hidden_size: int = 128
    tft_lstm_layers: int = 2
    tft_attention_heads: int = 4
    tft_dropout: float = 0.1
    
    # GNN parameters
    gnn_hidden_channels: int = 256
    gnn_num_layers: int = 3
    gnn_heads: int = 8
    
    # Training
    batch_size: int = 32
    epochs: int = 100
    learning_rate: float = 0.001
    device: str = "cuda" if os.getenv("USE_GPU", "false").lower() == "true" else "cpu"


@dataclass
class DataPaths:
    """File paths for data storage"""
    base_dir: str = "/home/claude"
    uploads_dir: str = "/mnt/user-data/uploads"
    outputs_dir: str = "/mnt/user-data/outputs"
    models_dir: str = os.path.join(base_dir, "models")
    cache_dir: str = os.path.join(base_dir, "cache")
    reports_dir: str = os.path.join(outputs_dir, "reports")


class NexusConfig:
    """Main configuration class aggregating all configs"""
    
    def __init__(self):
        self.grid = GridAPIConfig()
        self.pulsar = PulsarConfig()
        self.bigquery = BigQueryConfig()
        self.pinecone = PineconeConfig()
        self.llm = LLMConfig()
        self.aws = AWSConfig()
        self.firebase = FirebaseConfig()
        self.ml = MLConfig()
        self.paths = DataPaths()
    
    def validate(self) -> bool:
        """Validate that critical API keys are present"""
        required_keys = [
            ("GRID API", self.grid.api_key),
            ("Anthropic API", self.llm.anthropic_api_key),
        ]
        
        missing = [name for name, key in required_keys if not key]
        
        if missing:
            print(f"Warning: Missing API keys for: {', '.join(missing)}")
            print("Some features may be limited. Set environment variables to enable full functionality.")
            return False
        
        return True
    
    def create_directories(self):
        """Create necessary directories"""
        import os
        os.makedirs(self.paths.models_dir, exist_ok=True)
        os.makedirs(self.paths.cache_dir, exist_ok=True)
        os.makedirs(self.paths.reports_dir, exist_ok=True)


# Global configuration instance
config = NexusConfig()
