import logging
import sys
import os
import datetime

class IntervalFileHandler(logging.Handler):
    def __init__(self, base_dir="logs"):
        super().__init__()
        self.base_dir = base_dir
        self.current_filename = None
        self.current_file = None

    def _get_filename(self, record_time):
        dt = datetime.datetime.fromtimestamp(record_time)
        minute = (dt.minute // 5) * 5
        date_str = dt.strftime('%Y-%m-%d')
        hour_str = dt.strftime('%H')
        
        dir_path = os.path.join(self.base_dir, date_str, hour_str)
        os.makedirs(dir_path, exist_ok=True)
        
        
        file_name = f"{minute:02d}.log"
        return os.path.join(dir_path, file_name)

    def emit(self, record):
        try:
            filename = self._get_filename(record.created)
            
            if self.current_filename != filename:
                if self.current_file:
                    self.current_file.close()
                self.current_filename = filename
                self.current_file = open(self.current_filename, 'a', encoding='utf-8')
                
            msg = self.format(record)
            self.current_file.write(msg + '\n')
            self.current_file.flush()
        except Exception:
            self.handleError(record)
            
    def close(self):
        if self.current_file:
            self.current_file.close()
            self.current_file = None
            self.current_filename = None
        super().close()

def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        
        # File handler configured to store logs based on time logic
        file_handler = IntervalFileHandler(base_dir="logs")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger
