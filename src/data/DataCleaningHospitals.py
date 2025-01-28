import pandas as pd
import numpy as np
from geopy.geocoders import OpenCage
from geopy.extra.rate_limiter import RateLimiter

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

# POSTCODE DATA
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/processed/cleaned_postcode_data.csv"
# Load the CSV file into a DataFrame
postCodeDfSubset = pd.read_csv(file_path)
# Display the first few rows of the DataFrame to verify its content
postCodeDfSubset.head(1)
postCodeDfSubset.shape

# HOSPITAL DATA
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/raw/8-hopsital_locations_england.csv"
# Load the CSV file into a DataFrame
hospitalDf = pd.read_csv(file_path)
# Checking the shape of the original DataFrame
hospitalDf.shape
# Display the first few rows of the DataFrame to verify its content
hospitalDf.head()

# Dropping the unecessary column
hospitalDf.drop("Unnamed: 0", axis=1, inplace=True)
# Check the first few rows to verify the new columns
hospitalDf
hospitalDf.shape


# Set OpenCage API key
key = "9b8834f863c74335a225f0b8a7d02d90"
geocoder = OpenCage(key)

# Use RateLimiter to manage request frequency
geocode = RateLimiter(geocoder.reverse, min_delay_seconds=1)

# Prepare a list to hold the postcodes
postcodes = []

# Loop through each row in the DataFrame to get the postcode based on Latitude and Longitude
for index, row in hospitalDf.iterrows():
    # Formulate the query using latitude and longitude
    query = "{}, {}".format(row["Latitude"], row["Longitude"])

    # Perform the geocoding to get the result
    try:
        result = geocode(query)

        # Ensure the result is valid and extract components
        if result and "components" in result.raw:
            components = result.raw["components"]
            postcode = components.get(
                "postcode", np.nan
            )  # Use .get to avoid KeyError if 'postcode' is missing
        else:
            postcode = np.nan
    except Exception as e:
        print(f"Error geocoding {query}: {e}")
        postcode = np.nan

    postcodes.append(postcode)

# Add the postcodes as a new column to the DataFrame
hospitalDf["Postcode"] = postcodes

# Display the first few rows to verify
hospitalDf.head()

# Extract the first part of the postcode to create a new 'POSTCODE AREA' column
hospitalDf["Postcode area"] = hospitalDf["Postcode"].str.split(" ").str[0]

# Define the new order of columns
new_column_order = ["Postcode area", "Postcode", "Name", "Latitude", "Longitude"]
# Create a new DataFrame with columns in the desired order
hospitals = hospitalDf[new_column_order]
# Display the first few rows to verify the new column and its placement
hospitals.head()
hospitals.shape

# Filtering hospitalDf to include only rows where 'Postcode area' matches any of the London postcode districts
london_postcode_districts = postCodeDfSubset["Postcode district"].unique()
# Sorting the resulting DataFrame by 'Postcode' alphabetically and reset the index for the filtered DataFrame
hospitalsLdn = (
    hospitalDf[hospitalDf["Postcode area"].isin(london_postcode_districts)]
    .sort_values(by="Postcode")
    .reset_index(drop=True)
)
# Define the order of columns
columns_order = ["Postcode area", "Postcode", "Name", "Latitude", "Longitude"]
# Reorder the DataFrame according to the defined columns order
hospitalsLdn = hospitalsLdn[columns_order]

# Display the first few rows of the filtered and sorted DataFrame to verify
hospitalsLdn.head()
hospitalsLdn.shape

# Deduplicate postCodeDfSubset based on 'Postcode district', keeping the first occurrence
deduplicated_postCodeDfSubset = postCodeDfSubset.drop_duplicates(
    subset=["Postcode district"]
)

# Merge hospitalsLdn with the deduplicated postCodeDfSubset
merged_hospitals = hospitalsLdn.merge(
    deduplicated_postCodeDfSubset[["Postcode district", "District"]],
    left_on="Postcode area",
    right_on="Postcode district",
    how="left",
).drop(
    "Postcode district", axis=1
)  # Drop the merging key from postCodeDfSubset as it's redundant

# Display the first few rows of the merged DataFrame to verify the new 'Ward' column
merged_hospitals.head()


# File path where the CSV file will be saved, including the filename and extension
output_file_path = (
    "/Users/alessandrosuarez_/Desktop/cleanedDatasets/clean_hospitals_data.csv"
)
# Save the DataFrame to CSV
merged_hospitals.to_csv(output_file_path, index=False)
print(f"DataFrame saved to {output_file_path}")
