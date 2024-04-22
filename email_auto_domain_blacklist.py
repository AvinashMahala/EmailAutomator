class EmailAutoDomainBlacklist:
    def __init__(self, logging, blacklist_file):
        self.blacklist_file = blacklist_file
        self.logging=logging

    def read_blacklist_domains(self):
        try:
            with open(self.blacklist_file, 'r') as file:
                blacklist_domains = {line.strip() for line in file}
            return blacklist_domains
        except (FileNotFoundError, PermissionError) as e:
            self.logging.error(f"Error reading blacklist file: {e}")
            return set()