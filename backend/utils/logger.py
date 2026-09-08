import logging
from datetime import datetime

class BotLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.setup_logger()
    
    def setup_logger(self):
        """Setup logger with file and console handlers"""
        # Create logs directory if it doesn't exist
        import os
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Format
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # File handler
        log_file = f'logs/snapshield_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
    
    def info(self, message):
        self.logger.info(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def critical(self, message):
        self.logger.critical(message)

def get_logger(name):
    return BotLogger(name)
