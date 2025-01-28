import pandas as pd
import os

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

# POSTCODE DATA
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/processed/cleaned_postcode_data.csv"
# Load the CSV file into a DataFrame
postCodeDfSubset = pd.read_csv(file_path)
# Display the first few rows of the DataFrame to verify its content
postCodeDfSubset.head()

# Define the path to your directory containing the CSV files just once at the start
file_directory = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/raw/places"


def check_csv_column_consistency():
    # List all CSV files in the directory
    csv_files = [file for file in os.listdir(file_directory) if file.endswith(".csv")]

    # Initialize the column structure and a dictionary to hold discrepancies
    column_structure = None
    discrepancies = {}

    # Check if all CSV files have the same columns and identify differences
    for file_name in csv_files:
        df = pd.read_csv(os.path.join(file_directory, file_name))
        if column_structure is None:
            column_structure = set(df.columns)
        else:
            current_structure = set(df.columns)
            if column_structure != current_structure:
                # Store the differences
                discrepancies[file_name] = {
                    "extra": current_structure - column_structure,
                    "missing": column_structure - current_structure,
                }

    # Output the results
    if not discrepancies:
        print("All CSV files have the same columns.")
    else:
        print("Discrepancies found in the following files:")
        for file_name, diff in discrepancies.items():
            print(f"\n{file_name}:")
            print(f"Extra columns: {list(diff['extra'])}")
            print(f"Missing columns: {list(diff['missing'])}")


# Calling the function
check_csv_column_consistency()

# Define the list of required columns
required_columns = [
    "BusinessName",
    "BusinessType",
    "PostCode",
    "LocalAuthorityName",
    "Geocode/Longitude",
    "Geocode/Latitude",
]


def concatenate_csv_with_required_columns(required_columns):
    """
    Reads multiple CSV files from the specified directory, checks each file for required columns,
    and concatenates them into a single DataFrame.
    """
    # Initialize an empty list to store DataFrames
    dataframes_list = []

    # Loop through each file in the directory
    for file_name in os.listdir(file_directory):
        if file_name.endswith(".csv"):
            file_path = os.path.join(file_directory, file_name)
            # Read the CSV file
            df = pd.read_csv(file_path)
            # Filter the DataFrame for required columns and check if they exist
            if all(col in df.columns for col in required_columns):
                # Append the filtered DataFrame to the list
                dataframes_list.append(df[required_columns])
            else:
                print(
                    f"File {file_name} does not contain all required columns and will be skipped."
                )

    # Concatenate all DataFrames in the list into a single DataFrame
    if dataframes_list:
        return pd.concat(dataframes_list, ignore_index=True)
    else:
        return (
            pd.DataFrame()
        )  # Return an empty DataFrame if no files meet the requirements


# Calling the function
placesDf = concatenate_csv_with_required_columns(required_columns)
# sort by 'PostCode' and reset the index
placesDf = placesDf.sort_values(by="PostCode").reset_index(drop=True)
# Display the first few rows of the concatenated DataFrame
placesDf.head(3)
placesDf.shape
placesDf.isnull().sum()
placesDf.dtypes

# Merge placesDf with postCodeDfSubset to get the 'Ward' based on 'PostCode'
placesDf = placesDf.merge(
    postCodeDfSubset[["Postcode", "Ward"]],
    left_on="PostCode",
    right_on="Postcode",
    how="left",
)

# Drop the duplicate 'Postcode' column from postCodeDfSubset after merging
placesDf.drop("Postcode", axis=1, inplace=True)

# Checking the first few entries to verify the 'Ward' column is correctly merged
placesDf.head()
placesDf.shape

# Drop all rows with missing values
placesDf.dropna(inplace=True)

# Check the DataFrame after dropping missing values
placesDf.head()
placesDf["BusinessType"].unique()

# File path where the CSV file will be saved, including the filename and extension
output_file_path = (
    "/Users/alessandrosuarez_/Desktop/cleanedDatasets/cleaned_places_data.csv"
)
# Save the DataFrame to CSV
placesDf.to_csv(output_file_path, index=False)
print(f"DataFrame saved to {output_file_path}")
