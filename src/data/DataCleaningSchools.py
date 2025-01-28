import pandas as pd
from pyproj import Proj, transform

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

# SCHOOL DATA
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/raw/7-educationSchools.csv"
# Load the CSV file into a DataFrame
schoolsDf = pd.read_csv(file_path)
# Display the first few rows of the DataFrame to verify its content
schoolsDf.head()
schoolsDf.shape
schoolsDf.isnull().sum()

# Df subset with the needed features
schoolsDfSubset = schoolsDf[
    [
        "LA (name)",
        "Postcode",
        "EstablishmentName",
        "PhaseOfEducation (name)",
        "Gender (name)",
        "Easting",
        "Northing",
    ]
]
schoolsDfSubset.head()
schoolsDfSubset.shape

# Checking if all the districts are present in the school data
LA_values = schoolsDfSubset["LA (name)"].unique()

# Checking if these values are present in the 'District' column of postcodeDfSubset
is_present = postCodeDfSubset["District"].isin(LA_values)

# Printing the result to see if all values are present
print(f"All LA values are present in postCodeDfSubset 'District': {is_present.all()}")

# See which specific values are present or not
present_values = postCodeDfSubset["District"][is_present].unique()
missing_values = [value for value in LA_values if value not in present_values]

print(f"Present values: {present_values}")
print(f"Missing values from LA (name) in postCodeDfSubset 'District': {missing_values}")

# Drop rows from schoolsDfSubset where 'LA (name)' values do not match any values in postCodeDfSubset 'District'
schoolsDfSubset = schoolsDfSubset[schoolsDfSubset["LA (name)"].isin(present_values)]
schoolsDfSubset.shape

# Check for missing values in each column
schoolsDfSubset.isnull().sum()
# Directly drop rows with missing values in 'Postcode', 'Gender (name)', 'Easting', and 'Northing' columns in schoolsDfSubset
schoolsDfSubset.dropna(
    subset=["Postcode", "Gender (name)", "Easting", "Northing"], inplace=True
)
schoolsDfSubset.shape
# Check the count of missing values again to confirm
print(schoolsDfSubset.isnull().sum())
# Check the updated DataFrame to ensure the rows with missing values in specified columns are dropped
schoolsDfSubset.head()

# Create a new column 'Postcode Area' by extracting the initial part of the 'Postcode'
schoolsDfSubset["Postcode Area"] = schoolsDfSubset["Postcode"].str.extract(
    r"(^[\w\d]+)"
)

# Deduplicate postCodeDfSubset based on 'Postcode district', keeping the first occurrence
deduplicated_postCodeDfSubset = postCodeDfSubset.drop_duplicates(
    subset=["Postcode district"]
)

# Merge schoolsDfSubset with the deduplicated postCodeDfSubset
merged_schoolsDf = schoolsDfSubset.merge(
    deduplicated_postCodeDfSubset[["Postcode district", "Ward"]],
    left_on="Postcode Area",
    right_on="Postcode district",
    how="left",
).drop(
    "Postcode district", axis=1
)  # Drop the merging key from postCodeDfSubset as it's redundant

# New column order to place 'Ward' right after 'Postcode Area'
columns = list(merged_schoolsDf.columns)
ward_index = columns.index("Postcode Area") + 1  # Determine where to insert 'Ward'
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
merged_schoolsDf = merged_schoolsDf[new_column_order]

# Display the first few rows of the merged DataFrame to verify the new 'Ward' column
merged_schoolsDf.head()


def convert_osgb36_to_wgs84(easting, northing):
    # Define the projection for OSGB36 (using the EPSG code 27700)
    proj_osgb36 = Proj("epsg:27700")
    # Define the projection for WGS84 (using the EPSG code 4326)
    proj_wgs84 = Proj("epsg:4326")

    # Convert the coordinates
    longitude, latitude = transform(proj_osgb36, proj_wgs84, easting, northing)
    return longitude, latitude


# Apply the conversion function to each row
merged_schoolsDf["Longitude"], merged_schoolsDf["Latitude"] = zip(
    *merged_schoolsDf.apply(
        lambda row: convert_osgb36_to_wgs84(row["Easting"], row["Northing"]), axis=1
    )
)

# Now merged_schoolsDf have 'Longitude' and 'Latitude' columns added
merged_schoolsDf.head()


# Reorganise features order
cleanSchoolsDf = merged_schoolsDf[
    [
        "LA (name)",
        "Postcode",
        "Postcode Area",
        "Ward",
        "EstablishmentName",
        "PhaseOfEducation (name)",
        "Gender (name)",
        "Longitude",
        "Latitude",
    ]
]
cleanSchoolsDf.head()

# File path where the CSV file will be saved, including the filename and extension
output_file_path = (
    "/Users/alessandrosuarez_/Desktop/cleanedDatasets/clean_schools_data.csv"
)
# Save the DataFrame to CSV
cleanSchoolsDf.to_csv(output_file_path, index=False)
print(f"DataFrame saved to {output_file_path}")
