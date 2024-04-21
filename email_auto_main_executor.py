import csv
import os
import logging
from tabulate import tabulate
from dotenv import load_dotenv
from email_auto_csv_manager import EmailAutoCSVManager
from email_auto_domain_email_counter import EmailAutoDomainEmailCounter
from email_auto_email_sender import EmailAutoEmailSender
from email_auto_logger import EmailAutoLogger
from email_auto_file_manager import EmailAutoFileManager

class EmailAutoMainExecutor:
    def __init__(self):
        # Load environment variables from .env file
        EmailAutoLogger()
        load_dotenv()
        logging.info("---------------------------------------------------------------------------------------------------")
        logging.info("Email sending process started.")
        print("\nEmail sending process started.\n")

        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipientsFile = os.getenv('RECIPIENTS_FILE_PATH')
        self.email_subject_file = os.getenv('EMAIL_SUBJECT_FILE')
        self.email_body_file = os.getenv('EMAIL_BODY_FILE')
        self.attachment_path = os.getenv('ATTACHMENT_PATH')
        self.domain_limit = int(os.getenv('DOMAIN_LIMIT', 10))

        self.email_subject = EmailAutoFileManager.read_file(self.email_subject_file).strip()
        self.email_body_template = EmailAutoFileManager.read_file(self.email_body_file).strip()

        self.error_messages = []
        eaCSVMgrObj = EmailAutoCSVManager()
        email_send_status_dict = eaCSVMgrObj.read_email_send_status()
        eaEmailSenderObj = EmailAutoEmailSender(self.sender_email, self.sender_password)
        domain_email_counter = EmailAutoDomainEmailCounter()
        domain_email_count = domain_email_counter.read_domain_email_count()
        with open(self.recipientsFile, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                full_name = row['fullName']
                recipient_email = row['emailId']
                domain_email_count = domain_email_counter.track_domain_email_count(email_send_status_dict,recipient_email, domain_email_count)
                
                # Check if email is already sent
                if recipient_email in email_send_status_dict:
                    status = email_send_status_dict[recipient_email]['send_status']
                    if status == 'success':
                        # print(f"Email {email} has already been successfully sent.")
                        logging.info(f"Email {recipient_email} has already been successfully sent.")
                        continue
                    elif status == 'failure':
                        print(f"Email {recipient_email} has already failed to send.")
                        logging.warning(f"Email {recipient_email} has already failed to send.")
                        # Retry sending the email
                        try:
                            first_name = full_name.split()[0]
                            self.email_body_template = self.email_body_template.replace('[Placeholder]', first_name)
                            status = eaEmailSenderObj.send_email(recipient_email, full_name, self.email_subject,
                                                     self.email_body_template, self.attachment_path,
                                                     domain_email_count, self.domain_limit-1)
                            email_send_status_dict[recipient_email] = status
                        except Exception as e:
                            error_message = f"Error sending email to {recipient_email}: {e}"
                            print(error_message)
                            logging.error(error_message)
                            email_send_status_dict[recipient_email] = 'failure'
                        # Update email send status to CSV
                        eaCSVMgrObj.write_email_send_status()
                        
                        continue
                    else:
                        print(f"Unknown status for email {recipient_email}: {status}")
                        logging.warning(f"Unknown status for email {recipient_email}: {status}")
                        continue
                # Email has not been sent before, send it
                try:
                    first_name = full_name.split()[0]
                    self.email_body_template = self.email_body_template.replace('[Placeholder]', first_name)
                    status = eaEmailSenderObj.send_email(recipient_email, full_name, self.email_subject,
                                                     self.email_body_template, self.attachment_path,
                                                     domain_email_count, self.domain_limit-1)
                    email_send_status_dict[recipient_email] = status
                    logging.info(f"Status for email {recipient_email}: {status}")
                except Exception as e:
                    error_message = f"Error sending email to {recipient_email}: {e}"
                    print(error_message)
                    logging.error(error_message)
                    email_send_status_dict[recipient_email] = 'failure'
                # Update email send status to CSV after processing each email
                eaCSVMgrObj.write_email_send_status()

                # Wait for 2 seconds before sending the next email
                # time.sleep(2)
                
                
                
                # status = eaEmailSenderObj.send_email(recipient_email, full_name, self.email_subject,
                #                                      self.email_body_template, self.attachment_path,
                #                                      domain_email_count, self.domain_limit-1)
                email_send_status_dict[recipient_email] = status
                eaCSVMgrObj.write_email_send_status()

                if email_send_status_dict[recipient_email]['send_status'] == 'failure':
                    self.error_messages.append([full_name, recipient_email, status['send_status'], status['error_message']])

        if self.error_messages:
            headers = ['Full Name', 'Recipient Email', 'Send Status', 'Error Message']
            print("\nError Messages:")
            print(tabulate(self.error_messages, headers=headers, tablefmt='grid'))

        print("\nEmail sending process completed.\n")
        logging.info("Email sending process completed.")
        logging.info("---------------------------------------------------------------------------------------------------")
