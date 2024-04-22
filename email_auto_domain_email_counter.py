import csv
import os
from datetime import datetime
import logging

class EmailAutoDomainEmailCounter:
    DOMAIN_EMAIL_COUNT_FIELDS = ['domain', 'date', 'count']
    DOMAIN_EMAIL_COUNT_FILE = 'domainEmailCount.csv'
    BLACKLIST_FILE = 'blacklist_domains.txt'  # File to store blacklisted domains

    def __init__(self, logging):
        self.logging = logging

    def logINFO(self, message):
        self.logging.info(f"[{self.__class__.__name__}] {message}")

    def logERROR(self, message):
        self.logging.error(f"[{self.__class__.__name__}] {message}")

    def logWARNING(self, message):
        self.logging.warning(f"[{self.__class__.__name__}] {message}")

    def read_domain_email_count(self):
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
            self.logINFO("Successfully read domain email count file.")
        except (FileNotFoundError, PermissionError) as e:
            error_message = f"Error reading domain email count file: {e}"
            self.logging.error(error_message)
            self.logINFO(error_message)
        return domain_email_count

    def write_domain_email_count(self, domain_email_count):
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
            self.logINFO("Successfully wrote to domain email count file.")
        except (FileNotFoundError, PermissionError) as e:
            error_message = f"Error writing domain email count file: {e}"
            self.logERROR(error_message)

    def track_domain_email_count(self, email_send_status_dict, recipient_email, domain_email_count):
        domain = recipient_email.split('@')[-1]
        today = datetime.now().strftime('%Y-%m-%d')
        if domain not in domain_email_count:
            domain_email_count[domain] = {'date': today, 'count': 1}
        elif domain_email_count[domain]['date'] != today:
            domain_email_count[domain] = {'date': today, 'count': 1}
        else:
            domain_email_count[domain]['count'] += 1
        return domain_email_count

    def is_domain_limit_exceeded(self, domain_email_count, recipient_email, domain_limit):
        domain = recipient_email.split('@')[-1]
        today = datetime.now().strftime('%Y-%m-%d')
        if domain in domain_email_count and domain_email_count[domain]['date'] == today and domain_email_count[domain]['count'] > domain_limit:
            return True
        return False
    
    def add_to_blacklist(self, domain):
        try:
            with open(self.BLACKLIST_FILE, 'a') as file:
                file.write(domain + '\n')
            self.logWARNING(f"Domain {domain} added to blacklist.")
        except Exception as e:
            error_message = f"Error adding domain {domain} to blacklist: {e}"
            self.logERROR(error_message)

    def check_and_blacklist_domain(self, recipient_email, domain_email_count, domain_limit):
        domain = recipient_email.split('@')[-1]
        if domain in domain_email_count and domain_email_count[domain]['count'] == domain_limit+1:
            self.add_to_blacklist(domain)
