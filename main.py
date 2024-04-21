import csv
import os
import smtplib
import logging
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
from tabulate import tabulate
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(filename='email_sender.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to read content from a file
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Load environment variables from .env file
load_dotenv()

# Function to read email send status from CSV
def read_email_send_status():
    email_send_status = {}
    if not os.path.exists('emailSendStatus.csv'):
        with open('emailSendStatus.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['FullName', 'emailId', 'timestamp', 'send_status', 'delivery_status_code', 'retry_count', 'error_message', 'delivery_duration'])
    else:
        with open('emailSendStatus.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                email_send_status[row['emailId']] = {
                    'FullName': row['FullName'],
                    'timestamp': row['timestamp'],
                    'send_status': row['send_status'],
                    'delivery_status_code': row['delivery_status_code'],
                    'retry_count': int(row['retry_count']),
                    'error_message': row['error_message'],
                    'delivery_duration': row['delivery_duration']
                }
    return email_send_status

# Function to write email send status to CSV
def write_email_send_status(email_send_status):
    with open('emailSendStatus.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['FullName', 'emailId', 'timestamp', 'send_status', 'delivery_status_code', 'retry_count', 'error_message', 'delivery_duration'])
        writer.writeheader()
        for email, data in email_send_status.items():
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

# Function to read domain email count from CSV
def read_domain_email_count():
    domain_email_count = {}
    if os.path.exists('domainEmailCount.csv'):
        with open('domainEmailCount.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                domain_email_count[row['domain']] = {
                    'date': row['date'],
                    'count': int(row['count'])
                }
    return domain_email_count

# Function to write domain email count to CSV
def write_domain_email_count(domain_email_count):
    with open('domainEmailCount.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['domain', 'date', 'count'])
        writer.writeheader()
        for domain, data in domain_email_count.items():
            writer.writerow({
                'domain': domain,
                'date': data['date'],
                'count': data['count']
            })

# Function to track email sending count per domain
def track_domain_email_count(email_send_status, recipient_email, domain_email_count):
    domain = recipient_email.split('@')[-1]
    today = datetime.now().strftime('%Y-%m-%d')
    if domain not in domain_email_count:
        domain_email_count[domain] = {'date': today, 'count': 1}
    elif domain_email_count[domain]['date'] != today:
        domain_email_count[domain] = {'date': today, 'count': 1}
    else:
        domain_email_count[domain]['count'] += 1
    return domain_email_count

# Function to check if domain email limit exceeded
def is_domain_limit_exceeded(domain_email_count, recipient_email):
    domain = recipient_email.split('@')[-1]
    today = datetime.now().strftime('%Y-%m-%d')
    domain_limit = int(os.getenv('DOMAIN_LIMIT', 2))  # Default to 2 if DOMAIN_LIMIT is not set in .env
    if domain in domain_email_count and domain_email_count[domain]['date'] == today and domain_email_count[domain]['count'] >= domain_limit:
        return True
    return False

# Function to send email using SMTP
def send_email(sender_email, recipient_email, full_name, subject, body, attachment_path=None):
    try:
        # Read email send status from CSV
        email_send_status = read_email_send_status()

        # Read domain email count from CSV
        domain_email_count = read_domain_email_count()

        # Track email sending count per domain
        domain_email_count = track_domain_email_count(email_send_status, recipient_email, domain_email_count)

        # Check if domain email limit exceeded
        if is_domain_limit_exceeded(domain_email_count, recipient_email):
            domain = recipient_email.split('@')[-1]
            domain_limit = int(os.getenv('DOMAIN_LIMIT', 4))  # Default to 4 if DOMAIN_LIMIT is not set in .env
            error_message = f"Domain email limit exceeded for {domain}. Cannot send more than {domain_limit} emails per day to the same domain."
            headers = ['Full Name', 'Recipient Email', 'Send Status', 'Error Message']
            
            print(error_message)
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
        message['From'] = sender_email
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

        # Connect to Yahoo SMTP server and send email
        with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) as server:
            server.login(sender_email, 'qjnicfzyzkmtckdp')  # Update email and password
            server.send_message(message)

        print(f"Email sent to {recipient_email} (Recipient: {full_name}, Sender: {sender_email})")
        logging.info(f"Email sent to {recipient_email}")

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Update domain email count
        write_domain_email_count(domain_email_count)

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
        print(f"Error sending email to {recipient_email} (Recipient: {full_name}, Sender: {sender_email}): {error_message}")
        logging.error(error_message)
        # Retry sending the email after a simulated wait
        print("Waiting for 2 minutes before retrying...")
        time.sleep(60)  # Simulated wait for 5 seconds (replace with 120 for 2 minutes)
        # Error handling code here
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return {
            'FullName': full_name,
            'timestamp': timestamp,
            'send_status': 'failure',
            'delivery_status_code': 'AuthenticationError',
            'retry_count': 0,
            'error_message': str(e),
            'delivery_duration': '0 seconds'
        }
    except smtplib.SMTPException as e:
        error_message = f"SMTP error: {e}"
        print(f"Error sending email to {recipient_email} (Recipient: {full_name}, Sender: {sender_email}): {error_message}")
        logging.error(error_message)
        # Retry sending the email after a simulated wait
        print("Waiting for 2 minutes before retrying...")
        time.sleep(120)  # Simulated wait for 5 seconds (replace with 120 for 2 minutes)
        # Error handling code here
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return {
            'FullName': full_name,
            'timestamp': timestamp,
            'send_status': 'failure',
            'delivery_status_code': 'SMTPException',
            'retry_count': 0,
            'error_message': str(e),
            'delivery_duration': '0 seconds'
        }
    except Exception as e:
        error_message = f"Error sending email to {recipient_email} (Recipient: {full_name}, Sender: {sender_email}): {e}"
        print(error_message)
        logging.error(error_message)
        # Retry sending the email after a simulated wait
        # print("Waiting for 2 minutes before retrying...")
        # time.sleep(120)  # Simulated wait for 5 seconds (replace with 120 for 2 minutes)
        # Error handling code here
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return {
            'FullName': full_name,
            'timestamp': timestamp,
            'send_status': 'failure',
            'delivery_status_code': 'UnknownError',
            'retry_count': 0,
            'error_message': str(e),
            'delivery_duration': '0 seconds'
        }

def main():
    logging.info("Email sending process started.")
    print("\nEmail sending process started.\n")

    sender_email = 'avinash.mahala@yahoo.com'  # Replace with sender's Yahoo email address
    csv_file = 'recipients.csv'  # Path to CSV file containing recipient details
    email_subject_file = 'email_subject.txt'  # Path to text file containing email subject
    email_body_file = 'email_body.txt'  # Path to text file containing email body
    attachment_path = 'Avinash_Mahala_Resume.pdf'  # Path to the attachment file

    # Read email subject and body from files
    email_subject = read_file(email_subject_file).strip()
    email_body_template = read_file(email_body_file).strip()

    # Error messages list
    error_messages = []
    # Open CSV file and iterate over rows
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            full_name = row['fullName']
            email = row['emailId']

            # Send email
            status = send_email(sender_email, email, full_name, email_subject, email_body_template, attachment_path)

            # Log status
            # print(f"Status for email {email}: {status}")
            logging.info(f"Status for email {email}: {status}")
            # Write status to CSV
            email_send_status = read_email_send_status()
            email_send_status[email] = status
            write_email_send_status(email_send_status)

            # Check if there was an error
            if status['send_status'] == 'failure':
                error_messages.append([full_name, email, status['send_status'], status['error_message']])

    # Print error messages in tabular format
    if error_messages:
        headers = ['Full Name', 'Recipient Email', 'Send Status', 'Error Message']
        print("\nError Messages:")
        print(tabulate(error_messages, headers=headers, tablefmt='grid'))

    print("\nEmail sending process completed.\n")
    logging.info("Email sending process completed.")

# Entry point of the script
if __name__ == "__main__":
    main()
