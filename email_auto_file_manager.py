class EmailAutoFileManager:
    def __init__(self, logging):
        self.logging = logging

    def logINFO(self, message):
        self.logging.info(f"[{self.__class__.__name__}] {message}")

    def logERROR(self, message):
        self.logging.error(f"[{self.__class__.__name__}] {message}")

    def logWARNING(self, message):
        self.logging.warning(f"[{self.__class__.__name__}] {message}")

    def read_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError as e:
            error_message = f"File '{file_path}' not found: {e}"
            self.logERROR(error_message)
            return ""
        except Exception as e:
            error_message = f"Error reading file '{file_path}': {e}"
            self.logERROR(error_message)
            return ""
