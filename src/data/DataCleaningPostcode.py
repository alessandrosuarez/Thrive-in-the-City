import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

# POSTCODE DATA
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/raw/1-London postcodes.csv"
# Load the CSV file into a DataFrame
postCodeDf = pd.read_csv(file_path)
# Display the first few rows of the DataFrame to verify its content
postCodeDf.head()
postCodeDf.shape
# Checking for missing values in each column
postCodeDf.isnull().sum()
# Checking datatypes
postCodeDf.dtypes
# a list of all the columns of the dataset
postCodeDf.columns
# Creating a subset dataset containing all the needed features
postCodeDfSubset = postCodeDf[
    [
        "Postcode",
        "In Use?",
        "Latitude",
        "Longitude",
        "District",
        "Ward",
        "Ward Code",
        "District Code",
        "Lower layer super output area",
        "London zone",
        "Rural/urban",
        "Index of Multiple Deprivation",
        "Nearest station",
        "Distance to station",
        "Postcode district",
        "Average Income",
    ]
]

postCodeDfSubset.head()

# Remove not in use postcodes
postCodeDfSubset = postCodeDfSubset[postCodeDfSubset["In Use?"] != "No"]
postCodeDfSubset.head()
postCodeDfSubset.shape
# Drop 'In Use?' feature
postCodeDfSubset = postCodeDfSubset.drop(columns=["In Use?"])
postCodeDfSubset.head()

# Reorganise features order
postCodeDfSubset = postCodeDfSubset[
    [
        "District",
        "District Code",
        "Lower layer super output area",
        "Ward",
        "Ward Code",
        "Postcode",
        "Postcode district",
        "London zone",
        "Latitude",
        "Longitude",
        "Nearest station",
        "Distance to station",
        "Average Income",
        "Index of Multiple Deprivation",
        "Rural/urban",
    ]
]
postCodeDfSubset.head()

# File path where the CSV file will be saved, including the filename and extension
output_file_path = (
    "/Users/alessandrosuarez_/Desktop/cleanedDatasets/cleaned_postcode_data.csv"
)

# Save the DataFrame to CSV
postCodeDfSubset.to_csv(output_file_path, index=False)

print(f"DataFrame saved to {output_file_path}")
