import streamlit as st
import os
import pandas as pd
import numpy as np
import joblib
import pydeck as pdk
import matplotlib.pyplot as plt

# Define absolute paths to the model and data folders to run it in localhost
# base_dir = "/Users/alessandrosuarez_/Desktop/lastYRofUniShii/IndividualProjectIN3007/Deliverables/Workspace"
# models_folder = os.path.join(base_dir,"models")
# data_folder = os.path.join(base_dir,"data", "processed")

# Define absolute paths to the model and data folders to run it when app is deployed
models_folder = os.path.join("models")
data_folder = os.path.join("data", "processed")


# Function to load models and data
def load_resources():
    model = joblib.load(os.path.join(models_folder, "kmeans_model.pkl"))
    scaler = joblib.load(os.path.join(models_folder, "robust_scaler.joblib"))
    Q1_values = np.load(os.path.join(models_folder, "Q1_values.npy"))
    df = pd.read_csv(
        os.path.join(data_folder, "df_for_prediction_ui.csv")
    )  # df to get predictions
    full_df = pd.read_csv(
        os.path.join(data_folder, "df_with_clusters.csv")
    )  # df to add the predcitions
    cleaned_places_df = pd.read_csv(
        os.path.join(data_folder, "cleaned_places_data.csv")
    )
    clean_hospitals_df = pd.read_csv(
        os.path.join(data_folder, "clean_hospitals_data.csv")
    )
    clean_universities_df = pd.read_csv(
        os.path.join(data_folder, "clean_universities_data.csv")
    )
    cleaned_ethnicity_df = pd.read_csv(
        os.path.join(data_folder, "cleaned_ethniciy_data.csv")
    )
    cleaned_religion_df = pd.read_csv(
        os.path.join(data_folder, "cleaned_religion_data.csv")
    )
    cleaned_house_df = pd.read_csv(os.path.join(data_folder, "cleaned_house_data.csv"))
    cleaned_rent_df = pd.read_csv(os.path.join(data_folder, "clean_rent_data.csv"))
    clean_park_data_df = pd.read_csv(os.path.join(data_folder, "clean_park_data.csv"))
    clean_schools_df = pd.read_csv(os.path.join(data_folder, "clean_schools_data.csv"))
    cleaned_crime_df = pd.read_csv(os.path.join(data_folder, "cleaned_crime_data.csv"))

    return (
        model,
        scaler,
        Q1_values,
        df,
        full_df,
        cleaned_house_df,
        cleaned_rent_df,
        clean_park_data_df,
        clean_schools_df,
        cleaned_crime_df,
        cleaned_places_df,
        clean_hospitals_df,
        clean_universities_df,
        cleaned_ethnicity_df,
        cleaned_religion_df,
    )


# Loading resources
(
    model,
    scaler,
    Q1_values,
    df,
    full_df,
    cleaned_house_df,
    cleaned_rent_df,
    clean_park_data_df,
    clean_schools_df,
    cleaned_crime_df,
    cleaned_places_df,
    clean_hospitals_df,
    clean_universities_df,
    cleaned_ethnicity_df,
    cleaned_religion_df,
) = load_resources()


# Function to create charts
def create_bar_chart(data, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(15, 4))
    data.plot(kind="barh", color="red", ax=ax)

    # Customise y-axis labels
    ax.set_yticklabels(
        data.index, rotation=0, ha="right"
    )  # 'ha' is horizontal alignment
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.xaxis.grid(True, linestyle="--", which="major", color="grey", alpha=0.25)

    # Loop over the bars and add the text with the count
    for i, bar in enumerate(ax.patches):
        value = (
            bar.get_width()
        )  # Get the width of the bar (which is the count in this case)
        y = bar.get_y() + bar.get_height() / 2  # y position for the text
        ax.text(
            value if value >= 0 else 0,  # X position
            y,  # Y position
            f"{value:.2f}",  # Value to display
            va="center",  # Center alignment in the y direction
            ha=(
                "right" if value < 0 else "left"
            ),  # If value is negative, align right; else left
            fontsize=8,  # Font size
            color="black",
        )  # Text color

    plt.tight_layout()  # To adjust the plot to fit into the figure area.
    return fig


# Function that calculates the top ethnicities in Ward
def top_n_ethnicities(row, n):
    # This sort the values and return the top n as a Series
    return row.sort_values(ascending=False).head(n)


# Define a function to assign colors based on BusinessType
def color_by_business_type(business_type):
    color_map = {
        "Restaurant/Cafe/Canteen": [255, 0, 0, 255],  # Red
        "Retailers - other": [255, 255, 0, 255],  # Yellow
        "Takeaway/sandwich shop": [0, 128, 0, 255],  # Green
        "Pub/bar/nightclub": [0, 0, 255, 255],  # Blue
    }
    return color_map.get(business_type)


# Apply the function to create a new 'color' column in the DataFrame
cleaned_places_df["color"] = cleaned_places_df["BusinessType"].apply(
    color_by_business_type
)


# LAYOUT, TITLE AND CONTENT DESCRIPTION
st.set_page_config(page_title="Thrive in the City", page_icon="🏙️", layout="wide")
st.title("🌟 Thrive in the City 🌟")
st.markdown("## Welcome to your personal London neighborhood matchmaker!")
st.markdown(
    """
    🌟 Thrive in the City helps to **connect you with areas in London** that align perfectly with your lifestyle and desires.
    
    💷 Tackling the challenge of soaring living costs, **tailored recommendations** helping you navigate the city's eclectic neighborhoods with ease.
    
    🎉 **Dive in, discover your London**, and make living in this vibrant city uniquely yours.
    """
)


# SIDEBAR SLIDERS
st.sidebar.header("Your Preferences")  # Collect user preferences using sliders


# Initialize session state for default values
if "default_values" not in st.session_state:
    st.session_state["default_values"] = (
        Q1_values.copy()
    )  # Start with default Q1_values

# Use session_state for storing and retrieving current values
default_values = st.session_state["default_values"]

# Initialise all price and industry variables with default values
price_preference = st.sidebar.radio("Are you looking to rent or buy?", ("Rent", "Buy"))


# Dynamic sliders for rent or buy options
if price_preference == "Rent":
    rent_features = [3, 4, 5, 6]  # Indices for rent-related features
    rent_labels = [
        "Rent Price",
        "Budget-Friendly Rent Price",
        "Median Rent Price",
        "Premium Rents Price",
    ]
    rent_values = [1500, 1000, 1500, 2000]  # Default values for rent-related sliders
    for feature, label, default in zip(rent_features, rent_labels, rent_values):
        default_values[feature] = st.sidebar.slider(label, 0, 10000, default, 50)

elif price_preference == "Buy":
    buy_features = [7, 8, 9, 10, 11]  # Indices for buy-related features
    buy_labels = [
        "House Price",
        "Flat Price",
        "Terraced House Price",
        "Semi Detached Price",
        "Detached Price",
    ]
    buy_values = [
        500000,
        400000,
        450000,
        550000,
        750000,
    ]  # Default values for buy-related sliders
    for feature, label, default in zip(buy_features, buy_labels, buy_values):
        default_values[feature] = st.sidebar.slider(label, 0, 1000000, default, 1000)

st.sidebar.markdown("Prioritise Your Preferences:")
# Sliders for area description and personal lifestyle preferences
default_values[1] = st.sidebar.slider(
    "Area Comfort Level", 1, 10, 5, 1
)  # Deprivation index
default_values[2] = st.sidebar.slider("Crime Level", 0, 10, 5, 1)  # Total crimes
default_values[16] = st.sidebar.slider("Supermarkets", 0, 10, 5, 1)  # Grocery stores
default_values[17] = st.sidebar.slider(
    "Shops & Retail", 0, 10, 5, 1
)  # Shops and retail
default_values[26] = st.sidebar.slider("Schools", 0, 10, 5, 1)  # Education
default_values[27] = st.sidebar.slider("Hospitals", 0, 10, 5, 1)  # Healthcare
default_values[28] = st.sidebar.slider(
    "Arts, Entertainment & Recreation Places", 0, 10, 5, 1
)  # Arts and entertainment
default_values[29] = st.sidebar.slider("Green Areas", 0, 10, 5, 1)  # Parks

# Slider for average income
average_income = st.sidebar.slider(
    "Average Income",
    20000,
    200000,
    50000,
    5000,
    help="Set Your Average Income for Better Recommendations",
)
default_values[0] = average_income  # Index for 'Average Income'

st.sidebar.markdown("Select your work industry from the list below:")
# Checkboxes for industries
industry_factors = {
    "Agriculture, Forestry & Fishing": 12,
    "Manufacturing & Production": 13,
    "Building & Construction": 14,
    "Automotive Services": 15,
    "Grocery stores & Wholesale": 16,
    "Retail": 17,
    "Transportation & Storage": 18,
    "Hospitality": 19,
    "Tech & Communication": 20,
    "Finance & Insurance": 21,
    "Real Estate Services": 22,
    "Professional, Scientific & Technical": 23,
    "Business Administration & Support Services": 24,
    "Public Sector & Defence": 25,
    "Education": 26,
    "Healthcare Services": 27,
}

selected_industries = []
for industry, index in industry_factors.items():
    if st.sidebar.checkbox(industry, key=industry):
        selected_industries.append(index)

# Applying higher importance to selected industries
importance_factor = 2
for index in selected_industries:
    default_values[index] *= importance_factor


# MAIN LAYOUT
# Button to trigger the recommendation process
if st.sidebar.button("Find My Neighbourhood"):
    # Scale and predict the cluster
    input_features = np.array([default_values])
    scaled_features = scaler.transform(input_features)
    predicted_cluster = model.predict(scaled_features)

    # Display the predicted cluster
    st.write(f"Predicted cluster: {predicted_cluster[0]}")

    # Filter the full dataset for details corresponding to the predicted cluster
    recommended_neighbourhoods = full_df[
        full_df["Cluster_Labels"] == predicted_cluster[0]
    ]
    districts = recommended_neighbourhoods["District"].unique()

    # Store recommendations in session state for further interaction
    st.session_state["recommended_neighbourhoods"] = recommended_neighbourhoods
    st.session_state["districts"] = districts


# Display the recommendations
if (
    "recommended_neighbourhoods" in st.session_state
    and not st.session_state["recommended_neighbourhoods"].empty
):
    selected_district = st.selectbox(
        "#### Look at the matching Boroughs!", st.session_state["districts"]
    )

    if selected_district:
        # Filter for selected district details
        district_details = st.session_state["recommended_neighbourhoods"][
            st.session_state["recommended_neighbourhoods"]["District"]
            == selected_district
        ]
        # Retrieve unique wards within the selected district
        unique_wards = district_details["Ward"].unique()
        st.markdown(f"#### Insights for {selected_district}")
        # Placeholder for the District dropdown to populate it with visualization options
        district_insight = st.selectbox(
            "Select the data you want to visualise for the entire Borough:",
            [
                "Select",
                "Average House Price",
                "Average Rent Price",
                "Places",
            ],
            key=f"district_insight_{selected_district}",
        )
        # Placeholder for distict rendering visualization based on the type selected
        if district_insight != "Select":
            st.markdown(
                f"Placeholder for {district_insight} visualisation of {selected_district}"
            )
            # Render visualizations based on `district_insight`
            if district_insight == "Average House Price":
                # Filter the house price data for the selected district
                house_price_data = cleaned_house_df[
                    cleaned_house_df["District"] == selected_district
                ]

                # Converting the columns for better readability
                columns_to_convert = [
                    "Mean average price",
                    "Annual mean average flat price",
                    "Annual mean average terraced price",
                    "Annual mean average semi price",
                    "Annual mean average detached price",
                ]
                house_price_data[columns_to_convert] = (
                    house_price_data[columns_to_convert] / 10
                )  # Divides all values by 10

                house_price_data = house_price_data.drop(columns=["District"]).mean()

                # Create a bar chart for the house price data
                house_price_chart = create_bar_chart(
                    house_price_data,
                    title=f"Average House Price in {selected_district}",
                    xlabel="Mean Average Price (in thousands)",
                    ylabel="Property Type",
                )

                # Display the bar chart in the WebApp
                st.pyplot(house_price_chart)

            elif district_insight == "Average Rent Price":
                # Filter the rent price data for the selected district
                rent_price_data = cleaned_rent_df[
                    cleaned_rent_df["Borough"] == selected_district
                ]

                # Create a dictionary to hold the mean values for each house type
                house_types = [
                    "Room",
                    "Studio",
                    "One Bedroom",
                    "Two Bedrooms",
                    "Three Bedrooms",
                    "Four or More Bedrooms",
                ]
                mean_rent_prices = {}

                for house_type in house_types:
                    # DataFrame has Boolean columns for each house type that indicate whether each entry is of that type
                    # And a column "Average Rent Price" that contains the rent prices
                    if house_type in rent_price_data.columns:
                        mean_rent_prices[house_type] = rent_price_data.loc[
                            rent_price_data[house_type] == True, "Average Rent Price"
                        ].mean()

                # Convert the dictionary to a DataFrame for easy plotting
                mean_rent_prices_df = pd.DataFrame(
                    list(mean_rent_prices.items()),
                    columns=["House Type", "Average Rent Price"],
                )

                # Create a bar chart for the rent data
                rent_price_chart = create_bar_chart(
                    mean_rent_prices_df.set_index("House Type")["Average Rent Price"],
                    title=f"Average Rent Price by House Type in {selected_district}",
                    xlabel="Average Rent Price",
                    ylabel="Bedroom Category",
                )

                # Display the bar chart in the WebApp
                st.pyplot(rent_price_chart)

            elif district_insight == "Places":
                # Checkboxes for user to select which data to visualize
                show_places = st.checkbox("Places", value=True, key="places")
                show_green_spaces = st.checkbox("Show Green Spaces", key="green_spaces")
                show_hospitals = st.checkbox("Show Hospitals", key="hospitals")
                show_schools = st.checkbox("Show Schools", key="schools")
                show_universities = st.checkbox("Show Universities", key="universities")

                layers = []

                if show_places:
                    places_layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=cleaned_places_df[
                            (
                                cleaned_places_df["LocalAuthorityName"]
                                == selected_district
                            )
                            & (
                                cleaned_places_df["BusinessType"].isin(
                                    [
                                        "Restaurant/Cafe/Canteen",
                                        "Retailers - other",
                                        "Takeaway/sandwich shop",
                                        "Pub/bar/nightclub",
                                    ]
                                )
                            )
                        ],
                        get_position="[longitude, latitude]",
                        get_color="color",
                        get_radius=10,
                    )
                    layers.append(places_layer)
                if show_green_spaces:
                    green_spaces_layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=clean_park_data_df[
                            clean_park_data_df["District"] == selected_district
                        ],
                        get_position="[longitude, latitude]",
                        get_color="[0, 128, 0, 255]",  # Green
                        get_radius=50,
                    )
                    layers.append(green_spaces_layer)
                if show_hospitals:
                    hospitals_layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=clean_hospitals_df[
                            clean_hospitals_df["District"] == selected_district
                        ],
                        get_position="[longitude, latitude]",
                        get_color="[0, 0, 255, 255]",  # Blue
                        get_radius=50,
                    )
                    layers.append(hospitals_layer)
                if show_schools:
                    schools_layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=clean_schools_df[
                            clean_schools_df["LA (name)"] == selected_district
                        ],
                        get_position="[latitude, longitude]",
                        get_color="[255, 0, 0, 255]",  # Red
                        get_radius=50,
                    )
                    layers.append(schools_layer)
                if show_universities:
                    universities_layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=clean_universities_df[
                            clean_universities_df["Borough"] == selected_district
                        ],
                        get_position="[longitude, latitude]",
                        get_color="[255, 0, 0, 255]",  # Red
                        get_radius=50,
                    )
                    layers.append(universities_layer)

                if layers:
                    st.pydeck_chart(
                        pdk.Deck(
                            map_style="mapbox://styles/mapbox/light-v9",
                            initial_view_state=pdk.ViewState(
                                latitude=(
                                    cleaned_places_df["latitude"].mean()
                                    if show_places
                                    else 51.5074
                                ),  # Default to London's latitude
                                longitude=(
                                    cleaned_places_df["longitude"].mean()
                                    if show_places
                                    else -0.1278
                                ),  # Default to London's longitude
                                zoom=11,
                                pitch=0,
                            ),
                            layers=layers,
                        )
                    )
                else:
                    st.write("No layers selected or data is missing.")

        # Create a multi-column layout to display wards as cards
        columns = st.columns(2)
        for index, ward in enumerate(unique_wards):
            with columns[index % 2]:
                st.markdown(f"#### {ward}")
                # Placeholder for the ward dropdown to populate it with visualization options
                ward_insight = st.selectbox(
                    f"Explore in depth {ward}",
                    [
                        "Select",
                        "Crime Rate",
                        "Ethnicities",
                        "Religion",
                    ],
                    key=f"ward_{index}",
                )
                # Placeholder for rendering visualization based on the type selected
                if ward_insight != "Select":
                    st.markdown(
                        f"Placeholder for {ward_insight} visualization of {ward}"
                    )

                    # Render visualizations based on `ward_insight`
                    if ward_insight == "Crime Rate":
                        # Filter the crime data for the selected ward
                        ward_crime_data = (
                            cleaned_crime_df[cleaned_crime_df["Ward"] == ward]
                            .drop(columns=["Ward", "LSOA Name"])
                            .mean()
                        )

                        # Create a bar chart for the crime data
                        crime_chart = create_bar_chart(
                            ward_crime_data,
                            title=f"Crime Rate in {ward}",
                            xlabel="Average Reported Incidents",
                            ylabel="Crime Type",
                        )

                        # Display the bar chart in the WebApp
                        st.pyplot(crime_chart)

                    elif ward_insight == "Religion":
                        # Filter the religion data for the selected ward
                        ward_religion_data = (
                            cleaned_religion_df[cleaned_religion_df["Ward"] == ward]
                            .drop(columns=["Ward", "LSOA Name"])
                            .mean()
                        )

                        # Create a bar chart for the religion data
                        religion_chart = create_bar_chart(
                            ward_religion_data,
                            title=f"Religion Distribution in {ward}",
                            xlabel="Average Count",
                            ylabel="Religion",
                        )

                        # Display the bar chart in the WebApp
                        st.pyplot(religion_chart)

                    elif ward_insight == "Ethnicities":
                        # Filter the ethnicity data for the selected ward
                        ward_ethnicity_data = cleaned_ethnicity_df[
                            cleaned_ethnicity_df["Ward"] == ward
                        ].drop(columns=["Ward", "LSOA Name"])

                        # Now calculate the top n ethnicities for the selected ward
                        if not ward_ethnicity_data.empty:
                            # Get the series of top n ethnicities
                            top_ethnicities_series = top_n_ethnicities(
                                ward_ethnicity_data.iloc[0], 3
                            )

                            # Create a bar chart for the top n ethnicity data
                            ethnicity_chart = create_bar_chart(
                                top_ethnicities_series,
                                title=f"Top 3 Ethnicities in {ward}",
                                xlabel="Count",
                                ylabel="Ethnicity",
                            )

                            # Display the bar chart in the WebApp
                            st.pyplot(ethnicity_chart)

# Button to clear selections and recommendations
if st.button("Clear Selection"):
    # Reset relevant session state entries
    keys_to_reset = ["recommended_neighbourhoods", "districts", "default_values"]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    # Clear or reset the UI elements shown on the main page
    st.rerun()  # Rerun the app to reflect these changes
