import csv
import os
import logging
import shutil
from tabulate import tabulate
from dotenv import load_dotenv
from email_auto_csv_manager import EmailAutoCSVManager
from email_auto_domain_blacklist import EmailAutoDomainBlacklist
from email_auto_domain_email_counter import EmailAutoDomainEmailCounter
from email_auto_email_sender import EmailAutoEmailSender
from email_auto_email_stats import EmailAutoEmailStats
from email_auto_logger import EmailAutoLogger
from email_auto_file_manager import EmailAutoFileManager

class EmailAutoMainExecutor:
    def generate_pattern(pattern, repetitions):
        return pattern * repetitions

    PATTERN1 = generate_pattern("-", 100)
    PATTERN2 = generate_pattern("*", 100)
    PATTERN3 = generate_pattern("+", 100)
    PATTERN4 = generate_pattern("~", 100)

    def __init__(self):
        EmailAutoLogger()
        self.logging = logging
        self.logINFO(self.PATTERN1)
        self.logINFO("Email sending process started.")
        print("\nEmail sending process started.\n")

        # Create output directory if not exists
        output_directory = 'output'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Load environment variables from .env file
        try:
            load_dotenv()
            self.logINFO("Environment file loaded successfully!")
        except Exception as e:
            self.logERROR(f"Failed to load environment file: {e}")
            return

        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipientsFile = os.getenv('RECIPIENTS_FILE_PATH')
        self.email_subject_file = os.getenv('EMAIL_SUBJECT_FILE')
        self.email_body_file = os.getenv('EMAIL_BODY_FILE')
        self.attachment_path = os.getenv('ATTACHMENT_PATH')
        self.domain_limit = int(os.getenv('DOMAIN_LIMIT', 10))-1
        self.blacklist_file = os.getenv('BLACKLIST_FILE_PATH')  # Path to the blacklist file
        # self.email_send_status_file=os.getenv('EMAIL_SEND_STATUS_FILE_PATH')

        # Set recipients file path to the one in the output directory
        output_directory = 'output'
        recipients_file_name = os.path.basename(self.recipientsFile)
        output_recipients_file = os.path.join(output_directory, recipients_file_name.split('.')[0], recipients_file_name)

        # Use the copied recipients file from the output directory
        self.recipientsFile = output_recipients_file

        # Set email send status file name
        recipients_file_name = os.path.basename(self.recipientsFile)
        send_status_file_name = recipients_file_name.split('.')[0] + '_SendStatus.csv'
        self.email_send_status_file = os.path.join(output_directory, recipients_file_name.split('.')[0], send_status_file_name)

        # Create directory for recipient files if not exists
        recipient_directory = os.path.join(output_directory, recipients_file_name.split('.')[0])
        if not os.path.exists(recipient_directory):
            os.makedirs(recipient_directory)
        
        # Copy recipientsFile to recipient folder if not present already
        output_recipients_file = os.path.join(recipient_directory, os.path.basename(self.recipientsFile))
        if not os.path.exists(output_recipients_file):
            shutil.copy(self.recipientsFile, recipient_directory)


        # Use the corresponding created SendStatus csv file
        if not os.path.exists(self.email_send_status_file):
            with open(self.email_send_status_file, 'w', newline='') as csvfile:
                fieldnames = ['emailId', 'FullName', 'timestamp', 'send_status', 'delivery_status_code', 'retry_count', 'error_message', 'delivery_duration']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

        self.domain_email_count_file = os.getenv('DOMAIN_EMAIL_COUNT_CSV_FILE_PATH')

        self.eaFileMgrObj = EmailAutoFileManager(self.logging)

        self.email_subject = self.eaFileMgrObj.read_file(self.email_subject_file).strip()
        self.email_body_template = self.eaFileMgrObj.read_file(self.email_body_file).strip()

        self.error_messages = []
        eaCSVMgrObj = EmailAutoCSVManager(self.logging,self.email_send_status_file,self.domain_email_count_file)
        email_send_status_dict = eaCSVMgrObj.read_email_send_status()
        eaEmailSenderObj = EmailAutoEmailSender(self.logging, self.sender_email, self.sender_password)
        domain_email_counter = EmailAutoDomainEmailCounter(self.logging)
        domain_email_count = domain_email_counter.read_domain_email_count()

        domain_blacklist = EmailAutoDomainBlacklist(self.logging, self.blacklist_file)
        blacklist_domains = domain_blacklist.read_blacklist_domains()
        self.domain_email_recipients_file = self.recipientsFile
        self.eaEmailStatsObj= EmailAutoEmailStats(self.email_send_status_file,self.domain_email_recipients_file)
        self.eaEmailStatsObj.print_email_info()

        self.totalEmailCount=self.eaEmailStatsObj.get_total_emails()
        self.failedCount=self.eaEmailStatsObj.get_failed_emails()
        self.pendingCount=self.eaEmailStatsObj.get_pending_emails()
        self.successCount=self.eaEmailStatsObj.success_emails_count()

        with open(self.recipientsFile, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                full_name = row['fullName']
                recipient_email = row['emailId']

                self.start_action(f"processing email to {recipient_email}")
                self.start_action(f"Processing Email: {self.pendingCount+1}/{self.totalEmailCount}")

                # Check if recipient's domain is in the blacklist
                recipient_domain = recipient_email.split('@')[-1]
                if recipient_domain in blacklist_domains:
                    self.logWARNING(f"Skipping email to {recipient_email} as the domain is in the blacklist.")
                    print(f"Skipping email to {recipient_email} as the domain is in the blacklist.")
                    self.pendingCount+=1
                    continue
                
                domain_email_count = domain_email_counter.track_domain_email_count(email_send_status_dict,recipient_email, domain_email_count)
                
                # Check and blacklist domain if limit exceeded
                domain_email_counter.check_and_blacklist_domain(recipient_email, domain_email_count, self.domain_limit)

                # Check if email is already sent
                if recipient_email in email_send_status_dict:
                    status = email_send_status_dict[recipient_email]['send_status']
                    if status == 'success':
                        self.logWARNING(f"Email {recipient_email} has already been successfully sent.")
                        print(f"Email {recipient_email} has already been successfully sent.")
                        self.pendingCount+=1
                        continue
                    elif status == 'failure':
                        self.logWARNING(f"Email {recipient_email} has already failed to send.")
                        print(f"Email {recipient_email} has already failed to send.")
                        # Retry sending the email
                        try:
                            first_name = full_name.split()[0]
                            self.email_body_template_replaced=self.email_body_template.replace('[Placeholder]', first_name)
                            first_line = self.email_body_template_replaced.split('\n')[0]
                            self.logINFO(f"First line of body: {first_line}")
                            print(f"First line of body: {first_line}")
                            status = eaEmailSenderObj.send_email(recipient_email, full_name, self.email_subject,
                                                     self.email_body_template_replaced, self.attachment_path,
                                                     domain_email_count, self.domain_limit)
                            email_send_status_dict[recipient_email] = status
                            self.pendingCount+=1
                        except Exception as e:
                            error_message = f"Error sending email to {recipient_email}: {e}"
                            print(error_message)
                            self.action_failed("sending email", error_message)
                            email_send_status_dict[recipient_email] = 'failure'
                        # Update email send status to CSV
                        eaCSVMgrObj.write_email_send_status()
                        self.pendingCount+=1
                        continue
                    else:
                        self.logWARNING(f"Unknown status for email {recipient_email}: {status}")
                        print(f"Unknown status for email {recipient_email}: {status}")
                        self.pendingCount+=1
                        continue
                # Email has not been sent before, send it
                try:
                    first_name = full_name.split()[0]
                    self.email_body_template_replaced=self.email_body_template.replace('[Placeholder]', first_name)
                    first_line = self.email_body_template_replaced.split('\n')[0]
                    self.logINFO(f"First line of body: {first_line}")
                    print(f"First line of body: {first_line}")
                    status = eaEmailSenderObj.send_email(recipient_email, full_name, self.email_subject,
                                                     self.email_body_template_replaced, self.attachment_path,
                                                     domain_email_count, self.domain_limit)
                    email_send_status_dict[recipient_email] = status
                    self.logINFO(f"Status for email {recipient_email}: {status}")
                    self.pendingCount+=1
                except Exception as e:
                    error_message = f"Error sending email to {recipient_email}: {e}"
                    print(error_message)
                    self.action_failed("sending email", error_message)
                    email_send_status_dict[recipient_email] = 'failure'
                    self.pendingCount+=1
                # Update email send status to CSV after processing each email
                eaCSVMgrObj.write_email_send_status()

                status = eaEmailSenderObj.send_email(recipient_email, full_name, self.email_subject,
                                                     self.email_body_template, self.attachment_path,
                                                     domain_email_count, self.domain_limit)

                email_send_status_dict[recipient_email] = status
                eaCSVMgrObj.write_email_send_status()

                # Wait for 2 seconds before sending the next email
                # time.sleep(2)

                if email_send_status_dict[recipient_email]['send_status'] == 'failure':
                    self.error_messages.append([full_name, recipient_email, status['send_status'], status['error_message']])

                self.action_done(f"processing email to {recipient_email}")

        if self.error_messages:
            headers = ['Full Name', 'Recipient Email', 'Send Status', 'Error Message']
            print("\nError Messages:")
            print(tabulate(self.error_messages, headers=headers, tablefmt='grid'))

        print("\nEmail sending process completed.\n")
        self.logINFO("Email sending process completed.")
        self.logINFO(self.PATTERN3)
        self.eaEmailStatsObj.print_email_info()
        self.logINFO(self.PATTERN4)

    def logINFO(self, message):
        self.logging.info(f"[{self.__class__.__name__}] {message}")

    def logERROR(self, message):
        self.logging.error(f"[{self.__class__.__name__}] {message}")

    def logWARNING(self, message):
        self.logging.warning(f"[{self.__class__.__name__}] {message}")

    def start_action(self, action_name):
        log_message = f"Starting {action_name}..."
        self.logINFO(log_message)
        print(log_message)

    def action_done(self, action_name):
        log_message = f"{action_name} completed successfully."
        self.logINFO(log_message)
        print(log_message)

    def action_failed(self, action_name, error_message):
        log_message = f"{action_name} failed: {error_message}"
        self.logERROR(log_message)
        print(log_message)

