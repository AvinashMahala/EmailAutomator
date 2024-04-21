import csv
import logging
import os
import smtplib
import time
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tkinter import Button, Entry, Label, StringVar, Tk, ttk
from tkinter import messagebox as mbox
from tabulate import tabulate

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

# Function to send email using SMTP
def send_email():
    sender_email = sender_email_var.get()
    recipient_email = recipient_email_var.get()
    full_name = full_name_var.get()
    subject = subject_var.get()
    body = body_var.get()
    attachment_path = attachment_path_var.get()

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

        mbox.showinfo("Success", f"Email sent to {recipient_email} (Recipient: {full_name}, Sender: {sender_email})")

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = {
            'FullName': full_name,
            'emailId': recipient_email,
            'timestamp': timestamp,
            'send_status': 'success',
            'delivery_status_code': 'Delivered',
            'retry_count': 0,
            'error_message': '',
            'delivery_duration': '0 seconds'
        }
        email_send_status = read_email_send_status()
        email_send_status[recipient_email] = status
        write_email_send_status(email_send_status)
    except Exception as e:
        mbox.showerror("Error", f"Error sending email to {recipient_email} (Recipient: {full_name}, Sender: {sender_email}): {e}")

# GUI setup
root = Tk()
root.title("Email Sender")

# Variables for entry fields
sender_email_var = StringVar()
recipient_email_var = StringVar()
full_name_var = StringVar()
subject_var = StringVar()
body_var = StringVar()
attachment_path_var = StringVar()

# Labels
Label(root, text="Sender Email:").grid(row=0, column=0, padx=5, pady=5)
Label(root, text="Recipient Email:").grid(row=1, column=0, padx=5, pady=5)
Label(root, text="Full Name:").grid(row=2, column=0, padx=5, pady=5)
Label(root, text="Subject:").grid(row=3, column=0, padx=5, pady=5)
Label(root, text="Body:").grid(row=4, column=0, padx=5, pady=5)
Label(root, text="Attachment Path:").grid(row=5, column=0, padx=5, pady=5)

# Entry fields
Entry(root, textvariable=sender_email_var).grid(row=0, column=1, padx=5, pady=5)
Entry(root, textvariable=recipient_email_var).grid(row=1, column=1, padx=5, pady=5)
Entry(root, textvariable=full_name_var).grid(row=2, column=1, padx=5, pady=5)
Entry(root, textvariable=subject_var).grid(row=3, column=1, padx=5, pady=5)
Entry(root, textvariable=body_var).grid(row=4, column=1, padx=5, pady=5)
Entry(root, textvariable=attachment_path_var).grid(row=5, column=1, padx=5, pady=5)

# Send button
Button(root, text="Send Email", command=send_email).grid(row=6, columnspan=2, padx=5, pady=5)

root.mainloop()
