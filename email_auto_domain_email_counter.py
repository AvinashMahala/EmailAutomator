import csv
import os
from datetime import datetime

class EmailAutoDomainEmailCounter:
    DOMAIN_EMAIL_COUNT_FIELDS = ['domain', 'date', 'count']
    DOMAIN_EMAIL_COUNT_FILE = 'domainEmailCount.csv'

    @staticmethod
    def read_domain_email_count():
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
    def track_domain_email_count(email_send_status_dict, recipient_email, domain_email_count):
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
    def is_domain_limit_exceeded(domain_email_count, recipient_email, domain_limit):
        domain = recipient_email.split('@')[-1]
        today = datetime.now().strftime('%Y-%m-%d')
        if domain in domain_email_count and domain_email_count[domain]['date'] == today and domain_email_count[domain]['count'] > domain_limit:
            return True
        return False