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

# BUSINESS DATA
# Define the path to the CSV file
file_path = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace/data/raw/8.1-ukbusinessworkbook2023.csv"
# Load the CSV file into a DataFrame
businessDf = pd.read_csv(file_path)
# Display the first few rows of the DataFrame to verify its content
businessDf.head()
businessDf.shape

# Split 'Unnamed: 0' into two parts at the ':' and expand into separate columns
businessDf[["District Code", "District"]] = businessDf["Unnamed: 0"].str.split(
    ":", expand=True
)
# Strip whitespace from the new columns
businessDf["District Code"] = businessDf["District Code"].str.strip()
businessDf["District"] = businessDf["District"].str.strip()
# Drop the original 'Unnamed: 0' column
businessDf = businessDf.drop("Unnamed: 0", axis=1)
# Get a list of all column names in the DataFrame
columns = list(businessDf.columns)
# Move 'District Code' and 'District' to the front of the list
new_column_order = ["District Code", "District"] + [
    col for col in columns if col not in ["District Code", "District"]
]
# Reorder the DataFrame columns using the new order
businessDf = businessDf[new_column_order]
# Display the first few rows to verify the changes
businessDf.head()


# Filter businessDf to include only rows with 'District Code' that match those in postCodeDfSubset
filtered_businessDf = businessDf[
    businessDf["District Code"].isin(postCodeDfSubset["District Code"])
]
# Sort the filtered DataFrame alphabetically by the 'District' column
filtered_businessDf = filtered_businessDf.sort_values(by="District Code")
# Rename the columns with user-friendly names
filtered_businessDf = filtered_businessDf.rename(
    columns={
        "01-03 : Agriculture, forestry & fishing": "Agriculture, Forestry & Fishing",
        "05-39 : Production": "Manufacturing & Production",
        "41-43 : Construction": "Building & Construction",
        "45 : Motor trades": "Automotive Services",
        "46 : Wholesale": "Grocery stores & Wholesale",
        "47 : Retail": "Shops & Retail",
        "49-53 : Transport & Storage (inc postal)": "Transportation & Storage",
        "55-56 : Accommodation & food services": "Hotels & Restaurants",
        "58-63 : Information & communication": "Tech & Communication",
        "64-66 : Finance & insurance": "Finance & Insurance",
        "68 : Property": "Real Estate Services",
        "69-75 : Professional, scientific & technical": "Professional, Scientific & Technical",
        "77-82 : Business administration & support services": "Business Administration & Support Services",
        "84 : Public administration & defence": "Public Sector & Defence",
        "85 : Education": "Education",
        "86-88 : Health": "Healthcar Services",
        "90-99 : Arts, entertainment, recreation & other services": "Arts, Entertainment, Recreation & Other Services",
    }
)
# Display the first few rows of the filtered DataFrame to verify
filtered_businessDf
filtered_businessDf.shape
filtered_businessDf.columns

# File path where the CSV file will be saved, including the filename and extension
output_file_path = (
    "/Users/alessandrosuarez_/Desktop/cleanedDatasets/cleaned_businesses_data.csv"
)
# Save the DataFrame to CSV
filtered_businessDf.to_csv(output_file_path, index=False)
print(f"DataFrame saved to {output_file_path}")
