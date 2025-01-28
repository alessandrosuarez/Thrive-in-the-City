import pandas as pd
import numpy as np
from pyproj import Proj, transform
import geopandas as gpd
from shapely.geometry import Point
from sklearn.neighbors import BallTree
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
postCodeDfSubset["District"].unique()
postCodeDfSubset.shape

# GREEN SPACES
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/raw/8-GiGL_SpacesToVisit.csv"
# Load the CSV file into a DataFrame
greenAreasDf = pd.read_csv(file_path, encoding="cp1252")
# Checking the shape of the original df
greenAreasDf.shape
# Display the first few rows of the DataFrame to verify its content
greenAreasDf.head()
greenAreasDf.shape
greenAreasDf["PrimaryUse"].unique
greenAreasDf


# Creating a new subset DataFrame with only the specified columns
greenAreasDfSubset = greenAreasDf[["SiteName", "PrimaryUse", "Easting", "Northing"]]
# Displaying the first row of the subset DataFrame to verify its content
greenAreasDfSubset.head(1)
greenAreasDfSubset.shape


def convert_osgb36_to_wgs84(easting, northing):
    # Define the projection for OSGB36 (using the EPSG code 27700)
    proj_osgb36 = Proj(init="epsg:27700")
    # Define the projection for WGS84 (using the EPSG code 4326)
    proj_wgs84 = Proj(init="epsg:4326")

    # Convert the coordinates
    longitude, latitude = transform(proj_osgb36, proj_wgs84, easting, northing)
    return longitude, latitude


# Apply the conversion function to each row
greenAreasDfSubset["Longitude"], greenAreasDfSubset["Latitude"] = zip(
    *greenAreasDfSubset.apply(
        lambda row: convert_osgb36_to_wgs84(row["Easting"], row["Northing"]), axis=1
    )
)

# Now greenAreasDfSubset have "Longitude" and "Latitude" columns added
greenAreasDfSubset.head()

# Creating a new subset DataFrame with only the specified columns
parksDf = greenAreasDfSubset[["SiteName", "PrimaryUse", "Latitude", "Longitude"]]
parksDf.head()

# Convert parksDf and postCodeDfSubset to GeoDataFrames
gdf_parks = gpd.GeoDataFrame(
    parksDf, geometry=[Point(xy) for xy in zip(parksDf.Longitude, parksDf.Latitude)]
)
gdf_postcodes = gpd.GeoDataFrame(
    postCodeDfSubset,
    geometry=[
        Point(xy) for xy in zip(postCodeDfSubset.Longitude, postCodeDfSubset.Latitude)
    ],
)

# Convert the GeoDataFrame coordinates to radians for BallTree
gdf_parks["geometry_rad"] = gdf_parks["geometry"].apply(
    lambda x: (np.radians(x.y), np.radians(x.x))
)
gdf_postcodes["geometry_rad"] = gdf_postcodes["geometry"].apply(
    lambda x: (np.radians(x.y), np.radians(x.x))
)

# Create a BallTree for efficient spatial queries
tree = BallTree(np.array(list(gdf_postcodes["geometry_rad"])), metric="haversine")

# Query the BallTree for the nearest neighbour to each park
distances, indices = tree.query(np.array(list(gdf_parks["geometry_rad"])), k=1)

# Assign the closest postcodes to the parks DataFrame
parksDf["Closest Postcode"] = gdf_postcodes.iloc[indices.flatten()]["Postcode"].values

parksDf.head()

# Group the data by 'Closest Postcode' and count the number of parks in each postcode
park_counts_per_postcode = parksDf.groupby("Closest Postcode")["SiteName"].count()

# Display the count of parks for each postcode
print(park_counts_per_postcode)

# Filter the counts of postcodes with more than one park
postcodes_with_multiple_parks = park_counts_per_postcode[park_counts_per_postcode > 1]

# Display postcodes that have more than one park
print("Postcodes with more than one park:")
print(postcodes_with_multiple_parks)


# Get the distribution of the number of parks per postcode
distribution_of_parks_per_postcode = (
    park_counts_per_postcode.value_counts().sort_index()
)

# Print the total counts for postcodes with exactly 1, 2, 3, and 4 parks
print(
    f"There are {distribution_of_parks_per_postcode.get(1, 0)} postcodes with 1 park."
)
print(
    f"There are {distribution_of_parks_per_postcode.get(2, 0)} postcodes with 2 parks."
)
print(
    f"There are {distribution_of_parks_per_postcode.get(3, 0)} postcodes with 3 parks."
)
print(
    f"There are {distribution_of_parks_per_postcode.get(4, 0)} postcodes with 4 parks."
)


parksDf = parksDf.drop("PrimaryUse", axis=1)
parksDf.columns
parksDf.head(1)

# Create a new column 'Postcode District' by extracting the initial part of the 'Closest Postcode'
parksDf["Postcode District"] = parksDf["Closest Postcode"].str.extract(r"(^[\w\d]+)")

# Deduplicate postCodeDfSubset based on 'Postcode district', keeping the first occurrence
deduplicated_postCodeDfSubset = postCodeDfSubset.drop_duplicates(
    subset=["Postcode district"]
)

# Merge parksDf with the deduplicated postCodeDfSubset
merged_parksDf = parksDf.merge(
    deduplicated_postCodeDfSubset[["Postcode district", "District"]],
    left_on="Postcode District",
    right_on="Postcode district",
    how="left",
).drop(
    "Postcode district", axis=1
)  # Drop the merging key from postCodeDfSubset as it's redundant

# Display the first few rows of the merged DataFrame to verify the new 'Ward' column
merged_parksDf.head()

# Calculate the total number of parks per 'Closest Postcode'
merged_parksDf["Total parks in Postcode"] = merged_parksDf.groupby("Closest Postcode")[
    "SiteName"
].transform("count")

# Calculate the total number of parks per 'Postcode District'
merged_parksDf["Total parks in Postcode District"] = merged_parksDf.groupby(
    "Postcode District"
)["SiteName"].transform("count")

# Display the updated DataFrame to verify the new columns
merged_parksDf.head()
merged_parksDf.columns

# Extracting the unique Postcode Districts from both DataFrames
unique_parks_districts = merged_parksDf["Postcode District"].unique()
unique_postcode_districts = postCodeDfSubset["Postcode district"].unique()

# Checking if all parks' Postcode Districts are present in the postcode DataFrame
all_districts_present = np.isin(unique_parks_districts, unique_postcode_districts).all()

# Identifying any districts that are in merged_parksDf but not in postCodeDfSubset
missing_districts = unique_parks_districts[
    ~np.isin(unique_parks_districts, unique_postcode_districts)
]

# Generating the print statements
if all_districts_present:
    print(
        "All Postcode Districts in the parks dataset are present in the postcode dataset."
    )
else:
    print(
        f"Some Postcode Districts from the parks dataset are missing in the postcode dataset: {missing_districts}"
    )


# Extracting the unique Postcode Districts from both DataFrames
unique_postcode_districts = postCodeDfSubset["Postcode district"].unique()
unique_parks_districts = merged_parksDf["Postcode District"].unique()

# Checking if all postcodes' Districts from postCodeDfSubset are present in merged_parksDf
all_postcodes_present = np.isin(unique_postcode_districts, unique_parks_districts).all()

# Identifying any districts that are in postCodeDfSubset but not in merged_parksDf
missing_postcodes = unique_postcode_districts[
    ~np.isin(unique_postcode_districts, unique_parks_districts)
]

# Generating the print statements
if all_postcodes_present:
    print(
        "All Postcode Districts from the postcode dataset are present in the parks dataset."
    )
else:
    print(
        f"Some Postcode Districts from the postcode dataset are missing in the parks dataset: {missing_postcodes}"
    )


# File path where the CSV file will be saved, including the filename and extension
output_file_path = (
    "/Users/alessandrosuarez_/Desktop/cleanedDatasets/clean_park_data.csv"
)
# Save the DataFrame to CSV
merged_parksDf.to_csv(output_file_path, index=False)
print(f"DataFrame saved to {output_file_path}")
