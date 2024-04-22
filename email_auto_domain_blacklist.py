import logging

class EmailAutoDomainBlacklist:
    def __init__(self, logging, blacklist_file):
        self.blacklist_file = blacklist_file
        self.logging = logging

    def logINFO(self, message):
        self.logging.info(f"[{self.__class__.__name__}] {message}")

    def logERROR(self, message):
        self.logging.error(f"[{self.__class__.__name__}] {message}")

    def logWARNING(self, message):
        self.logging.warning(f"[{self.__class__.__name__}] {message}")


    def read_blacklist_domains(self):
        try:
            self.logINFO("Reading blacklist file...")
            with open(self.blacklist_file, 'r') as file:
                blacklist_domains = {line.strip() for line in file}
            return blacklist_domains
        except (FileNotFoundError, PermissionError) as e:
            error_message = f"Error reading blacklist file: {e}"
            self.logERROR(error_message)
            return set()
