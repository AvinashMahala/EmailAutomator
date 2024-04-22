import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
import time

from email_auto_domain_email_counter import EmailAutoDomainEmailCounter

class EmailAutoEmailSender:
    RETRY_MINUTES=120
    def __init__(self, logging, sender_email, sender_password):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.logging = logging
        self.eadEmailCounterObj = EmailAutoDomainEmailCounter(self.logging)
    
    def wait_and_retry(self, wait_time_seconds):
        self.logINFO(f"Waiting for {wait_time_seconds} seconds before retrying...")
        time.sleep(wait_time_seconds)
        self.logINFO("Retry initiated.")

    def logINFO(self, message):
        self.logging.info(f"[{self.__class__.__name__}] {message}")

    def logERROR(self, message):
        self.logging.error(f"[{self.__class__.__name__}] {message}")

    def logWARNING(self, message):
        self.logging.warning(f"[{self.__class__.__name__}] {message}")

    def start_action(self, action_name):
        self.logINFO(f"Starting {action_name}...")

    def action_done(self, action_name):
        self.logINFO(f"{action_name} completed successfully.")

    def action_failed(self, action_name, error_message):
        self.logERROR(f"{action_name} failed: {error_message}")

    def send_email(self, recipient_email, full_name, subject, body, attachment_path, domain_email_count, domain_limit):
        try:
            self.start_action("sending email")
            if self.eadEmailCounterObj.is_domain_limit_exceeded(domain_email_count, recipient_email, domain_limit):
                domain = recipient_email.split('@')[-1]
                error_message = f"Domain Email Limit Exceeded for {domain}. Limit: {domain_limit}/day."
                self.logERROR(error_message)
                return {
                    'FullName': full_name,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'send_status': 'failure',
                    'delivery_status_code': 'DomainEmailLimitExceeded',
                    'retry_count': 0,
                    'error_message': error_message,
                    'delivery_duration': '0 seconds'
                }
                
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            if attachment_path:
                with open(attachment_path, 'rb') as file:
                    part = MIMEApplication(file.read(), Name=attachment_path)
                part['Content-Disposition'] = f'attachment; filename="{attachment_path}"'
                message.attach(part)

            with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            self.action_done("sending email")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            self.eadEmailCounterObj.write_domain_email_count(domain_email_count)

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
            self.action_failed("sending email", error_message)
            self.wait_and_retry(self.RETRY_MINUTES)
            return self.handle_send_error(recipient_email, full_name, error_message)
        except smtplib.SMTPException as e:
            error_message = f"SMTP error: {e}"
            self.action_failed("sending email", error_message)
            self.wait_and_retry(self.RETRY_MINUTES)
            return self.handle_send_error(recipient_email, full_name, error_message)
        except Exception as e:
            error_message = f"Error sending email to {recipient_email}: {e}"
            self.action_failed("sending email", error_message)
            self.wait_and_retry(self.RETRY_MINUTES)
            return self.handle_send_error(recipient_email, full_name, error_message)

    def handle_send_error(self, recipient_email, full_name, error_message):
        self.logERROR(error_message)
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
