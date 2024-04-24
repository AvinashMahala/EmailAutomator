import csv

class EmailAutoEmailStats:
    def __init__(self, email_send_status_file, recipients_file):
        self.email_send_status_file = email_send_status_file
        self.recipients_file = recipients_file
        self.successEmailsCount=0

    def get_failed_emails(self):
        failed_emails = 0
        with open(self.email_send_status_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['send_status'] == 'failure':
                    failed_emails += 1
        return failed_emails

    def get_total_emails(self):
        total_emails = 0
        with open(self.recipients_file, 'r') as file:
            reader = csv.DictReader(file)
            total_emails = sum(1 for row in reader)
        return total_emails

    def get_pending_emails(self):
        total_emails = self.get_total_emails()
        sent_emails = 0
        with open(self.email_send_status_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['send_status'] == 'success':
                    sent_emails += 1
        pending_emails = sent_emails
        self.successEmailsCount=sent_emails
        return pending_emails

    def print_email_info(self):
        total_emails = self.get_total_emails()
        failed_emails = self.get_failed_emails()
        pending_emails = self.get_pending_emails()
        print(f"Total emails: {total_emails}")
        print(f"Failed emails: {failed_emails}")
        print(f"Pending emails: {pending_emails}")

    def success_emails_count(self):
        return self.successEmailsCount





