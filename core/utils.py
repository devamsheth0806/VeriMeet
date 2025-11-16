"""Utility functions for VeriMeet."""
import logging
from datetime import datetime
from typing import Dict, Any


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger("verimeet")


def log_external_call(service: str, action: str, details: Dict[str, Any] = None):
    """Log external API calls for demo clarity."""
    logger = logging.getLogger("verimeet.external")
    details_str = f" | Details: {details}" if details else ""
    logger.info(f"[EXTERNAL CALL] {service} - {action}{details_str}")


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()

