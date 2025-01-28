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


# RENT PRICE DATA
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/raw/4-London Rent.csv"
# Load the CSV file into a DataFrame
rentDf = pd.read_csv(file_path)
# Display the first few rows of the DataFrame to verify its content
rentDf.head()
# Checking the shape of the original df
rentDf.shape

# Dropping the columns with missing values (don't need them)
rentDf = rentDf.drop(
    columns=[
        "Count of rents",
        "Unnamed: 7",
        "Unnamed: 8",
        "Unnamed: 9",
        "Unnamed: 10",
        "Unnamed: 11",
        "Unnamed: 12",
        "Unnamed: 13",
        "Unnamed: 14",
        "Unnamed: 15",
    ]
)

# Renaming the specified columns
rentDf = rentDf.rename(
    columns={
        "Mean": "Average Rent Price",
        "Lower quartile": "Budget-Friendly Rent Price",
        "Upper quartile": "Premium Rents Price",
    }
)

# Get the unique values from the "Bedroom Category" column
rentDf["Bedroom Category"].unique()
# Print the columns of rentDf to verify the operations
rentDf.columns

# Drop rows where 'Bedroom Category' is nan
rentDf.dropna(subset=["Bedroom Category"], inplace=True)

# Perform one-hot encoding on the 'Bedroom Category' column
dummies = pd.get_dummies(rentDf["Bedroom Category"], prefix="", prefix_sep="")

# Updated column mapping to reflect the actual categories
column_mapping = {
    "Room": "Room",
    "Studio": "Studio",
    "One Bedroom": "One Bedroom",
    "Two Bedrooms": "Two Bedrooms",
    "Three Bedrooms": "Three Bedrooms",
    "Four or More Bedrooms": "Four or More Bedrooms",
}

# Rename the columns based on your mapping
dummies_renamed = dummies.rename(columns=column_mapping)

# Drop the original 'Bedroom Category' column from rentDf
rentDf.drop("Bedroom Category", axis=1, inplace=True)

# Now, concatenate the original rentDf with the dummies_renamed DataFrame
rentDf_with_dummies = pd.concat([rentDf, dummies_renamed], axis=1)

# New columns order
desired_order = [
    "Borough",
    "Room",
    "Studio",
    "One Bedroom",
    "Two Bedrooms",
    "Three Bedrooms",
    "Four or More Bedrooms",
    "Average Rent Price",
    "Budget-Friendly Rent Price",
    "Median",
    "Premium Rents Price",
]

# Reorder the DataFrame
rentDf_encoded = rentDf_with_dummies[desired_order]

# Verify the changes
rentDf_encoded
rentDf_encoded.isnull().sum()

# Extracting the unique values from the 'Borough' column of rentDf_encoded
borough_values = rentDf_encoded["Borough"].unique()

# Checking if these values are present in the 'District' column of postCodeSubset
is_present = postCodeDfSubset["District"].isin(borough_values)

# Identifying the specific Borough values that are missing in 'District'
missing_values = borough_values[
    ~np.isin(borough_values, postCodeDfSubset["District"].unique())
]

# Printing the complete list of missing values
if len(missing_values) > 0:
    print("Missing 'Borough' values in 'District':")
    for value in missing_values:
        print(value)
else:
    print("There are no missing 'Borough' values in 'District'.")

# File path where the CSV file will be saved, including the filename and extension
output_file_path = (
    "/Users/alessandrosuarez_/Desktop/cleanedDatasets/cleaned_rent_data.csv"
)
# Save the DataFrame to CSV
rentDf.to_csv(output_file_path, index=False)
print(f"DataFrame saved to {output_file_path}")


# HOUSE PRICE DATA
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/raw/5-Property sales overview.csv"
# Load the CSV file into a DataFrame
houseDf = pd.read_csv(file_path)
# Display the first few rows of the DataFrame to verify its content
houseDf.head()
# Checking the shape of the original df
houseDf.shape
houseDf.columns

# Creating a subset dataset containing all the needed features
housePriceDf = houseDf[
    [
        "Area",
        "Month",
        "Mean average price",
        "Annual mean average flat price",
        "Annual mean average terraced price",
        "Annual mean average semi price",
        "Annual mean average detached price",
    ]
]

housePriceDf.head()

# Convert "Month" to datetime, correctly handling the year
housePriceDf["Month"] = pd.to_datetime(
    housePriceDf["Month"], format="%b-%y", errors="coerce"
)

# Filter for entries with the date 2023-01-01 in the "Month" column
filtered_housePriceDf = housePriceDf[housePriceDf["Month"] == "2023-01-01"]

# Display the head of the filtered DataFrame to verify it contains only entries for January 2023
filtered_housePriceDf.head()

# Getting the unique 'Postcode district' values from postCodeDfSubset
postcode_district_values = postCodeDfSubset["Postcode district"].unique()

# Creating a mask to identify rows in grouped_df with 'Area' values not present in 'Postcode district' of postCodeDfSubset
missing_values_mask = ~filtered_housePriceDf["Area"].isin(postcode_district_values)

# Dropping these rows from grouped_df and resetting the index
grouped_df_cleaned = filtered_housePriceDf[~missing_values_mask].reset_index(drop=True)

# See the dropped 'Area' values, using the mask before resetting the index
dropped_values = filtered_housePriceDf[missing_values_mask]["Area"].unique()

# Showing the dropped 'Area' values
if len(dropped_values) > 0:
    print(
        "Dropped 'Area' values from filtered_housePriceDf not found in 'Postcode district' of postCodeDfSubset:"
    )
    for value in dropped_values:
        print(value)
else:
    print(
        "No 'Area' values were dropped from filtered_housePriceDf; all were found in 'Postcode district' of postCodeDfSubset."
    )

# Display the head and shape of the cleaned DataFrame to verify
grouped_df_cleaned.head(1000)
grouped_df_cleaned.shape

# Deduplicate PostCodeSubset based on 'Postcode district', keeping the first occurrence
deduplicated_PostCodeSubset = postCodeDfSubset.drop_duplicates(
    subset=["Postcode district"]
)

# Merge data_2023 with the deduplicated PostCodeSubset
data_2023_merged = grouped_df_cleaned.merge(
    deduplicated_PostCodeSubset[["Postcode district", "District"]],
    left_on="Area",
    right_on="Postcode district",
    how="left",
).drop(
    "Postcode district", axis=1
)  # Drop the 'Postcode district' column from data_2023_merged

# Specify the new column order to place 'District' right after 'Area'
columns = list(data_2023_merged.columns)
district_index = columns.index("Area") + 1  # Determine where to insert 'District'
new_column_order = (
    columns[:district_index]
    + ["District"]
    + [col for col in columns[district_index:] if col != "District"]
)

# Ensure 'Ward' is not duplicated in the new column order
new_column_order = [
    col
    for i, col in enumerate(new_column_order)
    if col != "District" or i == district_index
]

# Reorder the DataFrame using the new column order
data_2023_merged = data_2023_merged[new_column_order]
# Display the first few rows of the merged DataFrame to verify the new 'Ward' column
data_2023_merged.head(40)
data_2023_merged.columns

# File path where the CSV file will be saved, including the filename and extension
output_file_path = (
    "/Users/alessandrosuarez_/Desktop/cleanedDatasets/Test_house_data.csv"
)
# Save the DataFrame to CSV
data_2023_merged.to_csv(output_file_path, index=False)
print(f"DataFrame saved to {output_file_path}")
