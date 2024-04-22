import os
import re
import pandas as pd
from datetime import datetime

# Path to the directory containing your Excel files
directory_path = r"C:\Users\tran\OneDrive\Documents\marketresearch"

# Initialize an empty list to hold DataFrames
dataframes_list = []

# Loop over the files in the directory
for filename in os.listdir(directory_path):
    if filename.startswith("Market-research") and filename.endswith(".xlsx"):
        # Extract the date from the file name using regex
        match = re.search(r"(\d{4})(\d{2}).xlsx$", filename)
        if match:
            date_str = match.group(1) + "-" + match.group(2)
            # Read the Excel file into a DataFrame, skipping the first two rows beneath the header
            df = pd.read_excel(
                os.path.join(directory_path, filename), header=0, skiprows=[0, 1]
            )
            # Insert the 'Date' column at the beginning
            df.insert(0, "Date", datetime.strptime(date_str, "%Y-%m").date())
            # Append the DataFrame to the list
            dataframes_list.append(df)

# Combine all DataFrames into one
combined_df = pd.concat(dataframes_list)

# Save the combined DataFrame to a new Excel file
output_filename = os.path.join(directory_path, "combined_data.xlsx")
combined_df.to_excel(output_filename, index=False)
