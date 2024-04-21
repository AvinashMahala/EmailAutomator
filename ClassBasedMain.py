import sys
import csv
import os
import smtplib
import platform
import logging
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
from tabulate import tabulate
from dotenv import load_dotenv

class EmailAutoLogger:
    def __init__(self):
        self.logging=None
        # Create a directory to store log files if it doesn't exist
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
        self.logging=logging
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

class EmailAutoFileManager:
    @staticmethod
    def read_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()

class EmailAutoCSVManager:
    EMAIL_SEND_STATUS_FIELDS = ['emailId', 'FullName', 'timestamp', 'send_status', 'delivery_status_code', 'retry_count', 'error_message', 'delivery_duration']
    
    def __init__(self):
        """
        Initialize the EmailAutoCSVManager with necessary attributes.

        Args:
        """
        self.email_send_status_file = 'emailSendStatus.csv'
        self.domain_email_count_file = 'domainEmailCount.csv'
        self.email_send_status = {}
        self.domain_email_count = {}

    def read_email_send_status(self):
        """
        Read email send status from CSV file.
        """
        try:
            if not os.path.exists(self.email_send_status_file):
                with open(self.email_send_status_file, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(self.EMAIL_SEND_STATUS_FIELDS)
            else:
                with open(self.email_send_status_file, 'r') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        self.email_send_status[row['emailId']] = {
                            'FullName': row['FullName'],
                            'timestamp': row['timestamp'],
                            'send_status': row['send_status'],
                            'delivery_status_code': row['delivery_status_code'],
                            'retry_count': int(row['retry_count']),
                            'error_message': row['error_message'],
                            'delivery_duration': row['delivery_duration']
                        }
            return self.email_send_status
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error reading email send status file: {e}")

    def write_email_send_status(self):
        """
        Write email send status to CSV file.
        """
        try:
            with open(self.email_send_status_file, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.EMAIL_SEND_STATUS_FIELDS)
                writer.writeheader()
                for email, data in self.email_send_status.items():
                    writer.writerow({
                        'FullName': data['FullName'],
                        'emailId': email,
                        'timestamp': data['timestamp'],
                        'send_status': data['send_status'],
                        'delivery_status_code': data['delivery_status_code'],
                        'retry_count': data['retry_count'],
                        'error_message': data['error_message'],
                        'delivery_duration': data['delivery_duration']
                    })
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error writing email send status file: {e}")

class EmailAutoDomainEmailCounter:
    DOMAIN_EMAIL_COUNT_FIELDS = ['domain', 'date', 'count']
    DOMAIN_EMAIL_COUNT_FILE = 'domainEmailCount.csv'

    @staticmethod
    def read_domain_email_count():
        """
        Read domain email count from CSV file.
        """
        domain_email_count = {}
        try:
            if os.path.exists(EmailAutoDomainEmailCounter.DOMAIN_EMAIL_COUNT_FILE):
                with open(EmailAutoDomainEmailCounter.DOMAIN_EMAIL_COUNT_FILE, 'r') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        domain_email_count[row['domain']] = {
                            'date': row['date'],
                            'count': int(row['count'])
                        }
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error reading domain email count file: {e}")
        return domain_email_count

    @staticmethod
    def write_domain_email_count(domain_email_count):
        """
        Write domain email count to CSV file.
        """
        try:
            with open(EmailAutoDomainEmailCounter.DOMAIN_EMAIL_COUNT_FILE, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=EmailAutoDomainEmailCounter.DOMAIN_EMAIL_COUNT_FIELDS)
                writer.writeheader()
                for domain, data in domain_email_count.items():
                    writer.writerow({
                        'domain': domain,
                        'date': data['date'],
                        'count': data['count']
                    })
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error writing domain email count file: {e}")

    @staticmethod
    def track_domain_email_count(email_send_status, recipient_email, domain_email_count):
        """
        Track email sending count per domain.
        """
        domain = recipient_email.split('@')[-1]
        today = datetime.now().strftime('%Y-%m-%d')
        if domain not in domain_email_count:
            domain_email_count[domain] = {'date': today, 'count': 1}
        elif domain_email_count[domain]['date'] != today:
            domain_email_count[domain] = {'date': today, 'count': 1}
        else:
            domain_email_count[domain]['count'] += 1
        return domain_email_count

    @staticmethod
    def is_domain_limit_exceeded(domain_email_count, recipient_email, domain_limit=2):
        """
        Check if domain email limit exceeded.
        """
        domain = recipient_email.split('@')[-1]
        today = datetime.now().strftime('%Y-%m-%d')
        if domain in domain_email_count and domain_email_count[domain]['date'] == today and domain_email_count[domain]['count'] >= domain_limit:
            return True
        return False

class EmailAutoEmailSender:
    def __init__(self, sender_email, sender_password):
        self.sender_email = sender_email
        self.sender_password = sender_password


        # Read email send status from CSV
        eaCSVMgrObj=EmailAutoCSVManager()
        self.email_send_status_dict = eaCSVMgrObj.read_email_send_status()

    def send_email(self, recipient_email, full_name, subject, body, attachment_path,domain_email_count,domain_limit):
        try:
            # Check if domain email limit exceeded
            if EmailAutoDomainEmailCounter.is_domain_limit_exceeded(domain_email_count, recipient_email,domain_limit):
                domain = recipient_email.split('@')[-1]
                error_message = f"Domain Email Limit Exceeded for {domain}. Limit: {domain_limit}/day."
                headers = ['Full Name', 'Recipient Email', 'Send Status', 'Error Message']
                
                # print(error_message)
                logging.error(error_message)
                return {
                    'FullName': full_name,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'send_status': 'failure',
                    'delivery_status_code': 'DomainEmailLimitExceeded',
                    'retry_count': 0,
                    'error_message': error_message,
                    'delivery_duration': '0 seconds'
                }
                
            # Create a multipart message
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Subject'] = subject

            # Add body to email
            message.attach(MIMEText(body, 'plain'))

            if attachment_path:
                # Open and attach the file
                with open(attachment_path, 'rb') as file:
                    part = MIMEApplication(file.read(), Name=attachment_path)
                part['Content-Disposition'] = f'attachment; filename="{attachment_path}"'
                message.attach(part)

            # Connect to SMTP server and send email
            with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            logging.info(f"Email sent to {recipient_email}")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Update domain email count
            EmailAutoDomainEmailCounter.write_domain_email_count(domain_email_count)

            return {
                'FullName': full_name,
                'timestamp': timestamp,
                'send_status': 'success',
                'delivery_status_code': 'Delivered',
                'retry_count': 0,
                'error_message': '',
                'delivery_duration': '0 seconds'
            }
        except smtplib.SMTPAuthenticationError as e:
            error_message = f"SMTP authentication error: {e}"
            logging.error(error_message)
            return self.handle_send_error(recipient_email, full_name, error_message)
        except smtplib.SMTPException as e:
            error_message = f"SMTP error: {e}"
            logging.error(error_message)
            return self.handle_send_error(recipient_email, full_name, error_message)
        except Exception as e:
            error_message = f"Error sending email to {recipient_email}: {e}"
            logging.error(error_message)
            return self.handle_send_error(recipient_email, full_name, error_message)

    def handle_send_error(self, recipient_email, full_name, error_message):
        """
        Handle email sending errors, including logging and retry mechanisms.
        """
        logging.error(error_message)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return {
            'FullName': full_name,
            'timestamp': timestamp,
            'send_status': 'failure',
            'delivery_status_code': 'UnknownError',
            'retry_count': 0,
            'error_message': error_message,
            'delivery_duration': '0 seconds'
        }


class EmailAutoMainExecutor:
    def __init__(self):
        # Load environment variables from .env file
        eaLogger=EmailAutoLogger()
        logging=eaLogger.logging
        load_dotenv()
        logging.info("---------------------------------------------------------------------------------------------------")
        logging.info("Email sending process started.")
        print("\nEmail sending process started.\n")

        self.sender_email = os.getenv('SENDER_EMAIL')  # Replace with sender's Yahoo email address
        self.sender_pwd=os.getenv('SENDER_PASSWORD')
        self.recipientsFile = os.getenv('RECIPIENTS_FILE_PATH')  # Path to CSV file containing recipient details
        self.email_subject_file = os.getenv('EMAIL_SUBJECT_FILE')  # Path to text file containing email subject
        self.email_body_file = os.getenv('EMAIL_BODY_FILE')  # Path to text file containing email body
        self.attachment_path = os.getenv('ATTACHMENT_PATH')  # Path to the attachment file
        self.domain_limit = int(os.getenv('DOMAIN_LIMIT', 10))  # Default to 1 if DOMAIN_LIMIT is not set in .env
        # Read email subject and body from files
        self.email_subject = EmailAutoFileManager.read_file(self.email_subject_file).strip()
        self.email_body_template = EmailAutoFileManager.read_file(self.email_body_file).strip()

        # Error messages list
        self.error_messages = []
        # Write status to CSV
        eaCSVMgrObj=EmailAutoCSVManager()


        # Open CSV file and iterate over rows
        with open(self.recipientsFile, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                full_name = row['fullName']
                recipient_email = row['emailId']
                
                email_send_status_dict = eaCSVMgrObj.read_email_send_status()

                # Read domain email count from CSV
                self.domain_email_count = EmailAutoDomainEmailCounter.read_domain_email_count()
                # Track email sending count per domain
                self.domain_email_count = EmailAutoDomainEmailCounter.track_domain_email_count(email_send_status_dict, recipient_email, self.domain_email_count)
                

                # Send email
                eaEmailSenderObj=EmailAutoEmailSender(self.sender_email,self.sender_pwd)
                status = eaEmailSenderObj.send_email(recipient_email, full_name, self.email_subject, self.email_body_template, self.attachment_path,self.domain_email_count,self.domain_limit)

                # Log status
                # print(f"Status for email {email}: {status}")
                logging.info(f"Status for email {recipient_email}: {status}")
                
                email_send_status_dict[recipient_email] = status
                eaCSVMgrObj.write_email_send_status()

                # Check if there was an error
                if status['send_status'] == 'failure':
                    self.error_messages.append([full_name, recipient_email, status['send_status'], status['error_message']])

        # Print error messages in tabular format
        if self.error_messages:
            headers = ['Full Name', 'Recipient Email', 'Send Status', 'Error Message']
            print("\nError Messages:")
            print(tabulate(self.error_messages, headers=headers, tablefmt='grid'))


        print("\nEmail sending process completed.\n")
        logging.info("Email sending process completed.")
        logging.info("---------------------------------------------------------------------------------------------------")


# Entry point of the script
if __name__ == "__main__":
    app=EmailAutoMainExecutor()









