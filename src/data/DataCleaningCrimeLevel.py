import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

# POSTCODE DATA
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/processed/cleaned_postcode_data.csv"
# Load the CSV file into a DataFrame
postCodeDfSubset = pd.read_csv(file_path)
# Display the first few rows of the DataFrame to verify its content
postCodeDfSubset.head()
postCodeDfSubset.shape

# Crime Level
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/raw/4-Level Crime.csv"
# Load the CSV file into a DataFrame
crimeDf = pd.read_csv(file_path)
# Checking the shape of the original df
crimeDf.shape
# Display the first few rows of the DataFrame to verify its content
crimeDf.head()

# Calculate the number of missing values in each column
missing_values = crimeDf.isnull().sum()
# Filter columns that have at least one missing value and their counts
columns_with_missing_values = missing_values[missing_values > 0]
# Print the columns with missing values and how many missing values they have
print(columns_with_missing_values)


# Dropping the unnecessary columns
crimeDf = crimeDf.drop(columns=["LSOA Code", "Borough", "202401"])
pd.set_option("display.max_columns", None)
crimeDf.head(1)
print(list(crimeDf.columns))
crimeDf.shape


# Extracting the unique values from the 'LSOA Name' column of crimeDf
LSOA_values_crime = crimeDf["LSOA Name"].unique()
# Getting the unique 'Lower layer super output area' values from postCodeDfSubset
postcode_LSOA_values = postCodeDfSubset["Lower layer super output area"].unique()
# Creating a mask to identify rows in crimeDf with 'LSOA Name' values not present in 'Lower layer super output area' of postCodeDfSubset
missing_values_mask = ~crimeDf["LSOA Name"].isin(postcode_LSOA_values)
# Dropping these rows from crimeDf
crimeDfSubset = crimeDf[~missing_values_mask]
# Check the dropped values
dropped_values = crimeDf[missing_values_mask]["LSOA Name"].unique()
# Showing the dropped 'LSOA Name' values
if len(dropped_values) > 0:
    print(
        "Dropped 'LSOA Name' values from crimeDf not found in 'Lower layer super output area' of postCodeDfSubset:"
    )
    for value in dropped_values:
        print(value)
else:
    print(
        "No 'LSOA Name' values were dropped from crimeDf; all were found in 'Lower layer super output area' of postCodeDfSubset."
    )
# Now crimeDf_cleaned contains only the rows where 'LSOA Name' matches with 'Lower layer super output area' in postCodeDfSubset
pd.set_option("display.max_columns", None)
crimeDfSubset.head()
crimeDfSubset.shape


# 1. Identify columns for 2022 and 2023 using string matching
columns_2022_2023 = [
    col for col in crimeDfSubset.columns if "2022" in col or "2023" in col
]

# 2. Convert non-numeric data to numeric in these columns (if not already done)
for col in columns_2022_2023:
    crimeDfSubset[col] = pd.to_numeric(crimeDfSubset[col], errors="coerce").fillna(0)

# 3. Sum the identified columns into a new "Year 2022-2023" column
crimeDfSubset["Year 2022-2023"] = crimeDfSubset[columns_2022_2023].sum(axis=1)

# 4. Drop the original monthly columns for 2022 and 2023
crimeDfSubset.drop(columns=columns_2022_2023, inplace=True)

# DataFrame now contains the summed data for 2022 and 2023 in a new column,
# alongside the original 'LSOA Name', 'Major Category', and 'Minor Category' columns.

# Display the first few rows to verify the new structure
pd.set_option("display.max_columns", None)
crimeDfSubset.head(2)


# Get unique values in the 'Major Category' column
unique_major_categories = crimeDfSubset["Major Category"].unique()
# Print the unique values
print(unique_major_categories)


# Get unique values in the 'Minor Category' column
unique_major_categories = crimeDfSubset["Minor Category"].unique()
# Print the unique values
print(unique_major_categories)


# Drop the 'Minor Category' column
df = crimeDfSubset.drop(columns=["Minor Category"])

# Create a pivot table. This will convert 'Major Category' values into columns, index by 'LSOA Name', and fill with sums of 'Year 2022-2023'
pivot_df = df.pivot_table(
    index="LSOA Name",
    columns="Major Category",
    values="Year 2022-2023",
    aggfunc="sum",
    fill_value=0,
)
# Reset the index so 'LSOA Name' becomes a column again
pivot_df.reset_index(inplace=True)
# Remove the 'Major Category' name from the columns
pivot_df.columns.name = None
# Now pivot_df has 'Major Category' values as columns and their corresponding summed values
pivot_df.head()
pivot_df.columns


# Create a merge (join) between pivot_df and postCodeDfSubset
# The merge is based on matching 'LSOA Name' in pivot_df with 'Lower layer super output area' in postCodeDfSubset
# 'Ward' column from postCodeDfSubset is added to pivot_df in the process
# Deduplicate postCodeDfSubset based on 'Lower layer super output area', keeping the first occurrence
deduplicated_postCodeDfSubset = postCodeDfSubset.drop_duplicates(
    subset=["Lower layer super output area"]
)

# Merge pivot_df with the deduplicated postCodeDfSubset
merged_df = pivot_df.merge(
    deduplicated_postCodeDfSubset[["Lower layer super output area", "Ward"]],
    left_on="LSOA Name",
    right_on="Lower layer super output area",
    how="left",
).drop(
    "Lower layer super output area", axis=1
)  # Drop the merging key from postCodeDfSubset as it's redundant
# Specify the new column order to place 'Ward' right after 'LSOA Name'
columns = list(merged_df.columns)
ward_index = columns.index("LSOA Name") + 1  # Determine where to insert 'Ward'
new_column_order = (
    columns[:ward_index]
    + ["Ward"]
    + [col for col in columns[ward_index:] if col != "Ward"]
)

# Ensure 'Ward' is not duplicated in the new column order
new_column_order = [
    col for i, col in enumerate(new_column_order) if col != "Ward" or i == ward_index
]

# Reorder the DataFrame using the new column order
merged_df = merged_df[new_column_order]

# Display the first few rows of the merged DataFrame to verify the new 'Ward' column
merged_df.head()
merged_df.shape


# List of columns to sum up for 'Total Crimes'
crime_columns = [
    "Arson and Criminal Damage",
    "Burglary",
    "Drug Offences",
    "Miscellaneous Crimes Against Society",
    "Possession of Weapons",
    "Public Order Offences",
    "Robbery",
    "Theft",
    "Vehicle Offences",
    "Violence Against the Person",
]

# Create 'Total Crimes' column as the sum of all specified crime columns
merged_df["Total Crimes"] = merged_df[crime_columns].sum(axis=1)

# Drop the individual crime columns from the DataFrame
merged_df.drop(crime_columns, axis=1, inplace=True)

# Display the first few rows of the modified DataFrame to verify the changes
merged_df.head()


# File path where the CSV file will be saved, including the filename and extension
output_file_path = (
    "/Users/alessandrosuarez_/Desktop/cleanedDatasets/cleaned_crime_data.csv"
)
# Save the DataFrame to CSV
merged_df.to_csv(output_file_path, index=False)
print(f"DataFrame saved to {output_file_path}")
