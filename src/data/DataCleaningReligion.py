import pandas as pd
import numpy as np

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


# RELIGION
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/raw/3-Religion.csv"
# Load the CSV file into a DataFrame
religionDf = pd.read_csv(file_path)
# Display the first few rows of the DataFrame to verify its content
religionDf.head()
religionDf.shape

# Looping through the DataFrame columns and printing the datatype of each
for col in religionDf.columns:
    print(f"{col}: {religionDf[col].dtype}")

# Print a list of all column names in the DataFrame
print(list(religionDf.columns))

# Calculate the number of missing values in each column
missing_values = religionDf.isnull().sum()
# Filter columns that have at least one missing value and their counts
columns_with_missing_values = missing_values[missing_values > 0]
# Print the columns with missing values and how many missing values they have
print(columns_with_missing_values)

# Dropping the columns with missing values (don't need them)
religionDf = religionDf.drop(
    columns=[
        "Region code",
        "Region name",
        "Local authority code",
        "Local authority name",
        "MSOA Code",
        "MSOA Name",
        "LSOA Code",
        "Unnamed: 8",
        "All categories: Religion",
        "Other religion: Total",
        "No religion: Total",
    ]
)
pd.set_option("display.max_columns", None)
religionDf.head(1)
print(list(religionDf.columns))


# Extracting the unique values from the 'LSOA Name' column of ethniciyDfSubset
LSOA_values = religionDf["LSOA Name"].unique()
# Checking if these values are present in the 'Lower layer super output area' column of postCodeDfSubset
is_present = postCodeDfSubset["Lower layer super output area"].isin(LSOA_values)
# Identifying the specific LSOA values that are missing in 'Lower layer super output area'
missing_values = LSOA_values[
    ~np.isin(LSOA_values, postCodeDfSubset["Lower layer super output area"].unique())
]
# Printing the complete list of missing values
if len(missing_values) > 0:
    print("Missing 'LSOA Name' values in 'Lower layer super output area':")
    for value in missing_values:
        print(value)
else:
    print("There are no missing 'LSOA Name' values in 'Lower layer super output area'.")


# Convert non-numeric data to numeric across all applicable columns, except 'LSOA Name'
for col in religionDf.columns:
    if col not in ["LSOA Name"]:
        religionDf[col] = pd.to_numeric(religionDf[col], errors="coerce").fillna(0)

# Manually handle the aggregation for "Other religion" and "No religion"
# Sum all "Other religion:" columns
other_religion_columns = religionDf.columns[
    religionDf.columns.str.startswith("Other religion:")
]
religionDf["Other religion"] = religionDf[other_religion_columns].sum(axis=1)

# Sum all "No religion:" columns
no_religion_columns = religionDf.columns[
    religionDf.columns.str.startswith("No religion:")
]
religionDf["No religion"] = religionDf[no_religion_columns].sum(axis=1)

# Drop the original detailed religion columns
columns_to_drop = other_religion_columns.union(no_religion_columns)
religionDf.drop(columns=columns_to_drop, inplace=True)

# Assuming these main categories should be retained as is, based on your description
main_religion_categories = [
    "LSOA Name",
    "Christian",
    "Buddhist",
    "Hindu",
    "Jewish",
    "Muslim (Islam)",
    "Sikh",
    "Other religion",
    "No religion",
    "Religion not stated",
]

# Reorder the DataFrame
religionDfSubset = religionDf[main_religion_categories]

# Display the DataFrame to check the new structure
pd.set_option("display.max_columns", None)
religionDfSubset.head(2)
religionDfSubset.shape

# Deduplicate postCodeDfSubset based on 'Lower layer super output area'
deduplicated_postCodeDfSubset = postCodeDfSubset.drop_duplicates(
    subset=["Lower layer super output area"]
)

# Merge religionDfSubset with the deduplicated postCodeDfSubset
merged_df = religionDfSubset.merge(
    deduplicated_postCodeDfSubset[["Lower layer super output area", "Ward"]],
    left_on="LSOA Name",
    right_on="Lower layer super output area",
    how="left",
).drop(
    "Lower layer super output area", axis=1
)  # Drop the merging key

# Reordering the DataFrame
columns = list(merged_df.columns)
if "Ward" in columns:
    ward_index = columns.index("LSOA Name") + 1
    # Ensure 'Ward' is placed right after 'LSOA Name'
    new_column_order = (
        columns[:ward_index]
        + ["Ward"]
        + [col for col in columns[ward_index:] if col != "Ward"]
    )
    merged_df = merged_df[new_column_order]

# Display the first few rows and the shape of the merged DataFrame
merged_df.head()
merged_df.shape

# File path where the CSV file will be saved, including the filename and extension
output_file_path = (
    "/Users/alessandrosuarez_/Desktop/cleanedDatasets/cleaned_religion_data.csv"
)
# Save the DataFrame to CSV
merged_df.to_csv(output_file_path, index=False)
print(f"DataFrame saved to {output_file_path}")
