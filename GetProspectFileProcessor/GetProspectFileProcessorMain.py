import pandas as pd
import sqlite3
from pathlib import Path

# Define the filename of the CSV file
csv_filename = "./csvFiles/All_Contacts_2024_04_21_1.csv"

# Define the SQLite database filename
db_filename = "data.sqlite"

# Function to rename columns using camelCase
def camelcase(text):
    words = text.split()
    return words[0].lower() + ''.join(x.title() for x in words[1:])

# Function to rename columns without spaces
def rename_columns(df):
    # Rename columns using camelCase
    df.columns = [camelcase(col) for col in df.columns]
    return df

# Function to load data from CSV
def load_data(csv_filename):
    # Load CSV into a DataFrame
    df = pd.read_csv(csv_filename)
    # print(df)
    return df

# Function to perform data sanitization and validation
def clean_data(df):
    # Perform any necessary data cleaning and validation here
    # For example, you can check for missing values, correct data formats, etc.
    # You can also perform specific checks based on your knowledge of the data
    
    # For simplicity, let's assume we're just dropping rows with missing values
    # df.dropna(inplace=True)
    
    return df

# Function to check for duplicates
def check_duplicates(df):
    # Check for duplicates across the entire DataFrame
    duplicates = df[df.duplicated()]
    return duplicates

# Function to create or connect to SQLite database
def connect_to_database(db_filename):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_filename)
    return conn

# Function to create table and insert data into SQLite database
def insert_into_database(conn, df):
    # Insert DataFrame into SQLite database
    df.to_sql("data", conn, if_exists="replace", index=False)


# Function to load data from CSV files in a folder
def load_data_from_folder(folder_path):
    csv_files = Path(folder_path).glob("*.csv")
    for file in csv_files:
        print(f"Processing file: {file}")
        df = pd.read_csv(file)
        df = rename_columns(df)
        df_cleaned = clean_data(df)
        yield df_cleaned



        
# Main function
def main():
    # Load data from CSV
    df = load_data(csv_filename)
    # Rename columns without spaces
    df = rename_columns(df)
    
    # Clean data
    df_cleaned = clean_data(df)
    # print(df_cleaned)
    
    # Check for duplicates
    duplicates = check_duplicates(df_cleaned)
    if not duplicates.empty:
        print("Duplicate rows found:")
        print(duplicates)
    else:
        print("No duplicates found.")
    
    # Connect to SQLite database
    conn = connect_to_database(db_filename)
    
    # Insert data into database
    insert_into_database(conn, df_cleaned)
    
    # Close database connection
    conn.close()
    
    print("Data loaded into SQLite database.")

# Execute main function
if __name__ == "__main__":
    main()
