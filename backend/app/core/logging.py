import logging
import sys
from typing import Dict, Any


def setup_logging() -> None:
    """Configures structured logs for console output."""
    log_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    # Disable generic fastapi/uvicorn verbose logs if needed or align them
    logging.getLogger("uvicorn.error").handlers = [console_handler]
    logging.getLogger("uvicorn.access").handlers = [console_handler]


logger = logging.getLogger("voice_rag")
