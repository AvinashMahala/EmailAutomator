import csv
import os

class EmailAutoCSVManager:
    EMAIL_SEND_STATUS_FIELDS = ['emailId', 'FullName', 'timestamp', 'send_status', 'delivery_status_code', 'retry_count', 'error_message', 'delivery_duration']
    
    def __init__(self):
        self.email_send_status_file = 'emailSendStatus.csv'
        self.domain_email_count_file = 'domainEmailCount.csv'
        self.email_send_status_dict = {}
        self.domain_email_count = {}

    def read_email_send_status(self):
        try:
            if not os.path.exists(self.email_send_status_file):
                with open(self.email_send_status_file, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(self.EMAIL_SEND_STATUS_FIELDS)
            else:
                with open(self.email_send_status_file, 'r') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        self.email_send_status_dict[row['emailId']] = {
                            'FullName': row['FullName'],
                            'timestamp': row['timestamp'],
                            'send_status': row['send_status'],
                            'delivery_status_code': row['delivery_status_code'],
                            'retry_count': int(row['retry_count']),
                            'error_message': row['error_message'],
                            'delivery_duration': row['delivery_duration']
                        }
            return self.email_send_status_dict
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error reading email send status file: {e}")

    def write_email_send_status(self):
        try:
            with open(self.email_send_status_file, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.EMAIL_SEND_STATUS_FIELDS)
                writer.writeheader()
                for email, data in self.email_send_status_dict.items():
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