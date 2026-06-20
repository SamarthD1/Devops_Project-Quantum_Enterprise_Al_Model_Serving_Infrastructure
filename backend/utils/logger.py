import os
import json
import logging
import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
        }
        
        # Add exception details if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Add any extra properties passed to the log call
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
            
        return json.dumps(log_data)

def setup_logger():
    # Make sure logs directory exists
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "application.log")

    logger = logging.getLogger("quantum_backend")
    logger.setLevel(logging.INFO)
    logger.propagate = False # Avoid duplicate logging to root handlers

    # Clear existing handlers to prevent duplicate configurations
    if logger.handlers:
        logger.handlers.clear()

    formatter = JSONFormatter()

    # File Handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("Structured JSON Logging initialized successfully.")
    return logger
