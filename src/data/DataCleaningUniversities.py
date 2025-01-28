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

# UNIVERSITIES DATA
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/raw/8-learning-providers-plus.csv"
# Load the CSV file into a DataFrame
universitiesDf = pd.read_csv(file_path)
# Checking the shape of the original df
universitiesDf.shape
# Display the first few rows of the DataFrame to verify its content
universitiesDf.head()

universitiesDf["TOWN"].unique()
universitiesDf.columns


# Creating a new subset DataFrame with only the specified columns
universitiesDfSubset = universitiesDf[
    ["VIEW_NAME", "TOWN", "POSTCODE", "LONGITUDE", "LATITUDE", "EASTING", "NORTHING"]
]

# Displaying the first row of the subset DataFrame to verify its content
universitiesDfSubset.head(1)
universitiesDfSubset.shape

# Filter the DataFrame to include only universities in London
londonUniversitiesDf = universitiesDfSubset[
    universitiesDfSubset["TOWN"] == "LONDON"
].reset_index(drop=True)
# Display the first few rows of the filtered DataFrame to verify its content
londonUniversitiesDf.head()
londonUniversitiesDf.shape


# Extract the first part of the postcode to create a new 'POSTCODE AREA' column
londonUniversitiesDf["POSTCODE AREA"] = (
    londonUniversitiesDf["POSTCODE"].str.split(" ").str[0]
)
# Define the new order of columns, placing 'POSTCODE AREA' before 'POSTCODE'
new_column_order = ["POSTCODE AREA"] + [
    col for col in londonUniversitiesDf.columns if col != "POSTCODE AREA"
]
# Create a new DataFrame with columns in the desired order
londonUniversitiesDfReordered = londonUniversitiesDf[new_column_order]
# Display the first few rows to verify the new column and its placement
londonUniversitiesDfReordered.head()
londonUniversitiesDfReordered.shape

# Deduplicate postCodeDfSubset based on 'Postcode district', keeping the first occurrence
deduplicated_postCodeDfSubset = postCodeDfSubset.drop_duplicates(
    subset=["Postcode district"]
)

# Merge merged_UniversitiesDf with the deduplicated_postCodeDfSubset
# Use 'POSTCODE AREA' in merged_UniversitiesDf to join with 'Postcode district' in postCodeDfSubset
# Add 'District' from postCodeDfSubset as 'Borough' in merged_UniversitiesDf
merged_UniversitiesDf = londonUniversitiesDfReordered.merge(
    deduplicated_postCodeDfSubset[["Postcode district", "District"]],
    left_on="POSTCODE AREA",
    right_on="Postcode district",
    how="left",
).drop(
    "Postcode district",
    axis=1,  # Drop the merging key from postCodeDfSubset as it's redundant
)
# Renaming the 'District' column to 'Borough'
merged_UniversitiesDf.rename(columns={"District": "Borough"}, inplace=True)

# Specify the new column order to place 'Borough' (newly added column from 'District') right after 'POSTCODE AREA'
columns = list(merged_UniversitiesDf.columns)
borough_index = (
    columns.index("POSTCODE AREA") + 1
)  # Determine where to insert 'Borough'
new_column_order = (
    columns[:borough_index]
    + ["Borough"]
    + [col for col in columns[borough_index:] if col != "Borough"]
)

# Ensure 'Borough' is not duplicated in the new column order
new_column_order = [
    col
    for i, col in enumerate(new_column_order)
    if col != "Borough" or i == borough_index
]

# Reorder the DataFrame using the new column order
merged_UniversitiesDf = merged_UniversitiesDf[new_column_order]

# Display the first few rows of the merged DataFrame to verify the new 'Borough' column
merged_UniversitiesDf.head()
merged_UniversitiesDf.shape


# File path where the CSV file will be saved, including the filename and extension
output_file_path = (
    "/Users/alessandrosuarez_/Desktop/cleanedDatasets/clean_universities_data.csv"
)
# Save the DataFrame to CSV
merged_UniversitiesDf.to_csv(output_file_path, index=False)
print(f"DataFrame saved to {output_file_path}")
