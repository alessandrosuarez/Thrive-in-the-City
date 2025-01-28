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

# ETHNICITY
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/raw/2-EthnicityLSOA.csv"
# Load the CSV file into a DataFrame
ethnicityDf = pd.read_csv(file_path)
# Display the first few rows of the DataFrame to verify its content
ethnicityDf.head()
ethnicityDf.shape

# Checking datatypes
ethnicityDf.dtypes

# Extracting the unique values from the 'LSOA Name' column of ethniciyDfSubset
LSOA_values = ethnicityDf["LSOA Name"].unique()
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

# Filter ethnicityDf to include only rows where 'LSOA Name' matches 'Lower layer super output area' in postCodeDfSubset
ethnicityDfSubset = ethnicityDf[
    ethnicityDf["LSOA Name"].isin(postCodeDfSubset["Lower layer super output area"])
]
# Display the shape and the first few rows of the filtered DataFrame to verify
ethnicityDfSubset.head()
ethnicityDfSubset.shape
ethnicityDfSubset.isnull().sum()


# Dropping the columns with missing values (don't need them)
ethnicityDfSubset = ethnicityDfSubset.drop(
    columns=[
        "Region code",
        "Region name",
        "Local authority code",
        "Local authority name",
        "MSOA Code",
        "MSOA Name",
        "LSOA Code",
        "All categories: Ethnic group (detailed)",
    ]
)
ethnicityDfSubset.head()
ethnicityDfSubset.shape


# Extract unique ethnicities directly from the column names
unique_ethnicities = set()
for col in ethnicityDfSubset.columns:
    if (
        ":" in col
    ):  # This checks if the column name follows the pattern "Category: Ethnicity"
        ethnicity = col.split(":", 1)[1].strip()
        unique_ethnicities.add(ethnicity)

# Convert the set to a sorted list for consistency
unique_ethnicities = sorted(list(unique_ethnicities))

# Convert non-numeric data to numeric across all applicable columns, except a few like 'LSOA Name'
for col in ethnicityDfSubset.columns:
    if col not in ["LSOA Name"]:
        ethnicityDfSubset[col] = pd.to_numeric(
            ethnicityDfSubset[col], errors="coerce"
        ).fillna(0)

# Merge columns for each unique ethnicity
for ethnicity in unique_ethnicities:
    # Find and sum all columns that contain the ethnicity, case-insensitive
    columns_for_ethnicity = ethnicityDfSubset.columns[
        ethnicityDfSubset.columns.str.contains(ethnicity, case=False, regex=False)
    ]
    ethnicityDfSubset[ethnicity] = ethnicityDfSubset[columns_for_ethnicity].sum(axis=1)

# Drop original detailed ethnicity columns
# Construct a list of columns to keep
columns_to_keep = ["LSOA Name"] + unique_ethnicities
# Now drop everything else
religion_df = ethnicityDfSubset[columns_to_keep]

# Display the DataFrame to check the new structure
religion_df.head()
religion_df.shape


# Deduplicate postCodeDfSubset based on 'Lower layer super output area'
deduplicated_postCodeDfSubset = postCodeDfSubset.drop_duplicates(
    subset=["Lower layer super output area"]
)

# Merge religionDfSubset with the deduplicated postCodeDfSubset
merged_df = religion_df.merge(
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
    "/Users/alessandrosuarez_/Desktop/cleanedDatasets/cleaned_ethniciy_data.csv"
)
# Save the DataFrame to CSV
merged_df.to_csv(output_file_path, index=False)
print(f"DataFrame saved to {output_file_path}")
