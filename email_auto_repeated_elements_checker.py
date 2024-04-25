import pandas as pd

class RepeatedElementsChecker:
    def __init__(self):
        pass

    def has_duplicate_rows(self, csv_file):
        """
        Check if there are any duplicate rows in the CSV file.
        Returns True if duplicates are found, False otherwise.
        """
        df = pd.read_csv(csv_file)
        return df.duplicated().any()

    def find_duplicate_rows(self, csv_file):
        """
        Find all duplicate rows in the CSV file.
        Returns a DataFrame containing the duplicate rows.
        """
        df = pd.read_csv(csv_file)
        duplicates = df[df.duplicated()]
        return duplicates
    
    def count_duplicate_rows(self, csv_file):
        """
        Count the number of duplicate rows in the CSV file.
        Returns the count of duplicate rows.
        """
        df = pd.read_csv(csv_file)
        return df.duplicated().sum()
