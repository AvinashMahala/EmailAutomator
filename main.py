import csv
import os
import smtplib
import logging
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Configure logging
logging.basicConfig(filename='email_sender.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to read content from a file
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to read email send status from CSV
def read_email_send_status():
    email_send_status = {}
    if not os.path.exists('emailSendStatus.csv'):
        with open('emailSendStatus.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['emailId', 'status'])
            logging.info("Created emailSendStatus.csv file.")
    else:
        with open('emailSendStatus.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                email_send_status[row['emailId']] = row['status']
        logging.info("Loaded email send status from emailSendStatus.csv file.")
    return email_send_status

# Function to write email send status to CSV
def write_email_send_status(email_send_status):
    with open('emailSendStatus.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['emailId', 'status'])
        writer.writeheader()
        for email, status in email_send_status.items():
            writer.writerow({'emailId': email, 'status': status})
    logging.info("Updated email send status in emailSendStatus.csv file.")

# Function to send email using SMTP
def send_email(sender_email, recipient_email, subject, body, attachment_path=None):
    try:
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

        print(f"Email sent to {recipient_email}")
        logging.info(f"Email sent to {recipient_email}")
        return 'success'
    except smtplib.SMTPAuthenticationError as e:
        error_message = f"SMTP authentication error: {e}"
        print(error_message)
        logging.error(error_message)
        # Retry sending the email after a simulated wait
        print("Waiting for 2 minutes before retrying...")
        time.sleep(60)  # Simulated wait for 5 seconds (replace with 120 for 2 minutes)
        return 'failure'
    except smtplib.SMTPException as e:
        error_message = f"SMTP error: {e}"
        print(error_message)
        logging.error(error_message)
        # Retry sending the email after a simulated wait
        print("Waiting for 2 minutes before retrying...")
        time.sleep(120)  # Simulated wait for 5 seconds (replace with 120 for 2 minutes)
        return 'failure'
    except Exception as e:
        error_message = f"Error sending email to {recipient_email}: {e}"
        print(error_message)
        logging.error(error_message)
        # Retry sending the email after a simulated wait
        # print("Waiting for 2 minutes before retrying...")
        # time.sleep(120)  # Simulated wait for 5 seconds (replace with 120 for 2 minutes)
        return 'failure'

def main():
    logging.info("Email sending process started.")
    print("Email sending process started.")

    sender_email = 'avinash.mahala@yahoo.com'  # Replace with sender's Yahoo email address
    csv_file = 'recipients.csv'  # Path to CSV file containing recipient details
    email_subject_file = 'email_subject.txt'  # Path to text file containing email subject
    email_body_file = 'email_body.txt'  # Path to text file containing email body
    attachment_path = 'Avinash_Mahala_Resume.pdf'  # Path to the attachment file

    # Read email subject and body from files
    email_subject = read_file(email_subject_file).strip()
    email_body_template = read_file(email_body_file).strip()

    # Read email send status from CSV
    email_send_status = read_email_send_status()

    # Open CSV file and iterate over rows
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            full_name = row['fullName']
            email = row['emailId']

            # Check if email is already sent
            if email in email_send_status:
                status = email_send_status[email]
                if status == 'success':
                    # print(f"Email {email} has already been successfully sent.")
                    logging.info(f"Email {email} has already been successfully sent.")
                    continue
                elif status == 'failure':
                    print(f"Email {email} has already failed to send.")
                    logging.warning(f"Email {email} has already failed to send.")
                    # Retry sending the email
                    try:
                        first_name = full_name.split()[0]
                        email_body = email_body_template.replace('[Placeholder]', first_name)
                        status = send_email(sender_email, email, email_subject, email_body, attachment_path)
                        email_send_status[email] = status
                    except Exception as e:
                        error_message = f"Error sending email to {email}: {e}"
                        print(error_message)
                        logging.error(error_message)
                        email_send_status[email] = 'failure'
                    # Update email send status to CSV
                    write_email_send_status(email_send_status)
                    
                    continue
                else:
                    print(f"Unknown status for email {email}: {status}")
                    logging.warning(f"Unknown status for email {email}: {status}")
                    continue

            # Email has not been sent before, send it
            try:
                first_name = full_name.split()[0]
                email_body = email_body_template.replace('[Placeholder]', first_name)
                status = send_email(sender_email, email, email_subject, email_body, attachment_path)
                email_send_status[email] = status
            except Exception as e:
                error_message = f"Error sending email to {email}: {e}"
                print(error_message)
                logging.error(error_message)
                email_send_status[email] = 'failure'

            # Update email send status to CSV after processing each email
            write_email_send_status(email_send_status)

            # Wait for 2 seconds before sending the next email
            # time.sleep(2)

    logging.info("Email sending process completed.")
    print("Email sending process completed.")




# Entry point of the script
if __name__ == "__main__":
    main()
