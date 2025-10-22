"""
Smart model loader with automatic caching.

This module provides intelligent model loading that:
- Checks for locally cached models first
- Downloads from HuggingFace Hub if not found
- Automatically caches downloaded models for future use
"""

import os
import logging
from pathlib import Path
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Model configuration
HUGGINGFACE_MODEL_NAME = "jinaai/jina-embeddings-v3"
LOCAL_MODEL_DIR = "./models/jina-embeddings-v3"


def check_local_model_exists(model_path: str) -> bool:
    """
    Verify if a valid model exists at the specified path.
    
    Args:
        model_path: Path to local model directory
        
    Returns:
        True if model exists with all required files, False otherwise
    """
    model_dir = Path(model_path)
    
    if not model_dir.exists():
        return False
    
    # Check for essential model files
    required_files = ["config.json", "modules.json"]
    
    for file in required_files:
        if not (model_dir / file).exists():
            logger.warning(f"Missing required file: {file}")
            return False
    
    # Check for model weights (either .bin or .safetensors)
    has_weights = (
        (model_dir / "pytorch_model.bin").exists() or
        any(model_dir.glob("*.safetensors"))
    )
    
    if not has_weights:
        logger.warning("Missing model weights file")
        return False
    
    return True


def download_model_to_local(model_name: str, local_path: str) -> bool:
    """
    Download model from HuggingFace Hub and save locally.
    
    Args:
        model_name: HuggingFace model identifier
        local_path: Destination path for model files
        
    Returns:
        True if download and save successful, False otherwise
    """
    try:
        logger.info(f"Downloading model: {model_name}")
        logger.info(f"Target directory: {local_path}")
        logger.info("This may take a few minutes...")
        
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        
        model = SentenceTransformer(
            model_name,
            trust_remote_code=True,
            cache_folder=None
        )
        
        model.save(local_path)
        
        logger.info(f"Model downloaded and saved to: {os.path.abspath(local_path)}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        return False


def load_model_smart(model_path: str = None) -> SentenceTransformer:
    """
    Load embedding model with automatic caching.
    
    Loading strategy:
    1. If model_path is a valid local directory, load from there
    2. Otherwise, check default cache directory (./models/jina-embeddings-v3)
    3. If not cached, download from HuggingFace Hub and save to cache
    4. Load and return the model
    
    Args:
        model_path: Model identifier (HuggingFace name or local path)
        
    Returns:
        Loaded SentenceTransformer model instance
        
    Raises:
        Exception: If model cannot be loaded from any source
    """
    if model_path is None:
        model_path = HUGGINGFACE_MODEL_NAME
    
    logger.info(f"Loading model: {model_path}")
    
    # Case 1: Check if model_path is a local directory
    if os.path.exists(model_path) and os.path.isdir(model_path):
        if check_local_model_exists(model_path):
            logger.info(f"Found local model at: {model_path}")
            try:
                model = SentenceTransformer(model_path, trust_remote_code=True)
                logger.info("Model loaded successfully from local path")
                return model
            except Exception as e:
                logger.error(f"Failed to load from {model_path}: {e}")
                logger.info("Will try to download fresh model...")
    
    # Case 2: Check default cache directory
    if check_local_model_exists(LOCAL_MODEL_DIR):
        logger.info(f"Found model in cache: {LOCAL_MODEL_DIR}")
        try:
            model = SentenceTransformer(LOCAL_MODEL_DIR, trust_remote_code=True)
            logger.info("Model loaded successfully from cache")
            return model
        except Exception as e:
            logger.error(f"Failed to load from cache: {e}")
            logger.info("Will try to download fresh model...")
    
    # Case 3: Download from HuggingFace
    logger.info("Model not found locally, downloading from HuggingFace...")
    
    model_name = model_path if "/" in model_path else HUGGINGFACE_MODEL_NAME
    
    success = download_model_to_local(model_name, LOCAL_MODEL_DIR)
    
    if not success:
        # Fallback: load directly from HuggingFace
        logger.warning("Could not cache model, loading directly from HuggingFace")
        try:
            model = SentenceTransformer(model_name, trust_remote_code=True)
            logger.info("Model loaded from HuggingFace (not cached)")
            return model
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    # Load the downloaded model
    try:
        model = SentenceTransformer(LOCAL_MODEL_DIR, trust_remote_code=True)
        logger.info("Model loaded successfully from cache")
        return model
    except Exception as e:
        logger.error(f"Failed to load downloaded model: {e}")
        raise

