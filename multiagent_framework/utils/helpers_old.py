"""
Helper utilities for the multiagent framework.
"""

import logging
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


def validate_config(config_dict: Dict[str, Any], required_fields: list) -> tuple[bool, str]:
    """
    Validate agent configuration dictionary.
    
    Args:
        config_dict: Agent configuration to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["name", "model_type"]
    
    # Check required fields
    is_valid, error = validate_config(config_dict, required_fields)
    if not is_valid:
        return is_valid, error
    
    # Validate model type
    valid_model_types = ["kimi", "qwen", "custom"]
    if config_dict["model_type"] not in valid_model_types:
        return False, f"Invalid model_type. Must be one of: {valid_model_types}"
    
    # Validate numeric fields
    numeric_fields = {
        "max_tokens": (100, 4000),
        "temperature": (0.0, 1.0),
        "timeout": (10, 300),
        "retry_attempts": (1, 10)
    }
    
    for field, (min_val, max_val) in numeric_fields.items():
        if field in config_dict:
            try:
                value = float(config_dict[field])
                if not (min_val <= value <= max_val):
                    return False, f"Field '{field}' must be between {min_val} and {max_val}"
            except (ValueError, TypeError):
                return False, f"Field '{field}' must be a number"
    
    return True, ""
    """
    Validate configuration dictionary.
    
    Args:
        config_dict: Configuration to validate
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    for field in required_fields:
        if field not in config_dict:
            return False, f"Missing required field: {field}"
        
        if config_dict[field] is None or config_dict[field] == "":
            return False, f"Field '{field}' cannot be empty"
    
    return True, ""


def format_response(response: str, max_length: Optional[int] = None) -> str:
    """
    Format response text for display.
    
    Args:
        response: Response text to format
        max_length: Maximum length to truncate to
        
    Returns:
        Formatted response text
    """
    if not response:
        return "No response available"
    
    # Clean up the response
    formatted = response.strip()
    
    # Truncate if needed
    if max_length and len(formatted) > max_length:
        formatted = formatted[:max_length] + "..."
    
    return formatted


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers,
        force=True
    )
    
    return logging.getLogger(__name__)


def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load JSON file safely.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Loaded data or None if error
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading JSON file {file_path}: {str(e)}")
        return None


def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save data to JSON file safely.
    
    Args:
        data: Data to save
        file_path: Path to save file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON file {file_path}: {str(e)}")
        return False


def load_yaml_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load YAML file safely.
    
    Args:
        file_path: Path to YAML file
        
    Returns:
        Loaded data or None if error
    """
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError) as e:
        logging.error(f"Error loading YAML file {file_path}: {str(e)}")
        return None


def save_yaml_file(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save data to YAML file safely.
    
    Args:
        data: Data to save
        file_path: Path to save file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        return True
    except Exception as e:
        logging.error(f"Error saving YAML file {file_path}: {str(e)}")
        return False


def sanitize_input(text: str) -> str:
    """
    Sanitize input text for processing.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = text.strip()
    
    # Remove control characters except newlines and tabs
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\t')
    
    return sanitized


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension (without dot)
    """
    return Path(filename).suffix.lstrip('.')


def is_valid_api_key(api_key: str) -> bool:
    """
    Basic validation for API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if format appears valid, False otherwise
    """
    if not api_key:
        return False
    
    # Basic checks
    if len(api_key) < 10:  # Too short
        return False
    
    if api_key.isspace():  # Only whitespace
        return False
    
    # Should contain alphanumeric characters
    if not any(c.isalnum() for c in api_key):
        return False
    
    return True


def format_execution_time(seconds: float) -> str:
    """
    Format execution time for display.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


def create_directory_structure(base_path: str, structure: Dict[str, Any]) -> bool:
    """
    Create directory structure from dictionary.
    
    Args:
        base_path: Base directory path
        structure: Dictionary defining directory structure
        
    Returns:
        True if successful, False otherwise
    """
    try:
        base = Path(base_path)
        
        for name, content in structure.items():
            path = base / name
            
            if isinstance(content, dict):
                # Directory
                path.mkdir(parents=True, exist_ok=True)
                create_directory_structure(str(path), content)
            else:
                # File
                path.parent.mkdir(parents=True, exist_ok=True)
                if content is not None:
                    path.write_text(str(content))
                else:
                    path.touch()
        
        return True
    except Exception as e:
        logging.error(f"Error creating directory structure: {str(e)}")
        return False