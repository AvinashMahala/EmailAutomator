import os
import logging
from datetime import datetime

class EmailAutoLogger:
    def __init__(self):
        # Create log folder
        log_directory = self.create_log_folder()
        os.makedirs(log_directory, exist_ok=True)
        # Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        # Generate a unique session ID
        session_id = self.generate_session_id()
        # Define the log file name with the current date
        log_file = os.path.join(log_directory, f"email_sender_{current_date}.log")
        # Configure logging with the dynamic log file name
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        # Log session start details
        logging.info(f"Session ID: {session_id}")
        logging.info(f"Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def generate_session_id(self):
        # Generate a unique session ID based on the current timestamp
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def create_log_folder(self):
        # Get the current year and month
        current_year = datetime.now().strftime("%Y")
        current_month = datetime.now().strftime("%B")
        # Create the log folder if it doesn't exist
        log_directory = os.path.join("application_logs", current_year, current_month)
        os.makedirs(log_directory, exist_ok=True)
        return log_directory