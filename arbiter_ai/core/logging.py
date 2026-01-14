import logging
from typing import Optional

def configure_logging(
    level: int = logging.WARNING,
    format: Optional[str] = None,
    handler: Optional[logging.Handler] = None,
) -> None:
    """Configure Arbiter logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format: Custom log format string
        handler: Custom handler (default: StreamHandler)
        
    Example:
        >>> from arbiter_ai import configure_logging
        >>> import logging
        >>> configure_logging(level=logging.DEBUG)
    """
    logger = logging.getLogger("arbiter")
    logger.setLevel(level)
    
    if not logger.handlers:
        h = handler or logging.StreamHandler()
        fmt = format or "%(levelname)s:%(name)s:%(message)s"
        h.setFormatter(logging.Formatter(fmt))
        logger.addHandler(h)