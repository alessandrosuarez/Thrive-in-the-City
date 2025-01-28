# Installation Instructions

## Prerequisites
- **Python:** This project requires Python 3.6 or higher. Download Python from [https://www.python.org/downloads/](https://www.python.org/downloads/).
- **pip:** Ensure that pip is installed along with Python.

## Step 1: Set Up a Virtual Environment
Create and activate a virtual environment to manage the dependencies for the project.
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

## Step 2: Install Required Packages
Install all dependencies listed in the requirements.txt file using pip and environment.yml for conda environments.
```bash
pip install -r requirements.txt
```

## Step 3: Run the Application
Finally, run the application using Streamlit. The application's entry point is `app.py`:
```bash
streamlit run app.py
```
To use the deployed web application:
https://thriveinthecity.streamlit.app/

# Python Imports in the Project
The following Python libraries are used throughout the project:
- streamlit
- os
- pandas
- numpy
- joblib
- pydeck
- matplotlib.pyplot
- matplotlib.cm
- sklearn (various modules)
- geopy.geocoders
- geopy.extra.rate_limiter
- pyproj
- geopandas
- shapely.geometry
- scipy

# Project Structure

The project is organized into several directories and files:

- `app.py`: The main Streamlit application script that can be launched with the command.
- `data/`: This directory contains all the data used in the project.
  - `evaluation_images/`: Contains images used for evaluating models or results.
  - `processed/`: Includes processed data files that have been cleaned and transformed for analysis.
  - `raw/`: Raw data files as obtained from the original sources.
- `models/`: Contains the machine learning models saved as `.pkl` files, and scaler objects.
  - `old_models/`: Archive of previous versions of models.
- `notebooks/`: Jupyter notebooks where the data merging and model training processes are documented.
  - `Clustering_postcode_level.ipynb`: Notebook detailing clustering at the postcode level.
  - `Clustering_ward_level.ipynb`: Notebook for ward-level clustering.
  - `Clustering_ward_level_Phase_2.ipynb`: Continuation of ward-level clustering, phase 2.
- `src/`: Contains the proprietary source code for the project.
  - `data/`: Scripts for data cleaning and preprocessing tasks, such as:
    - `DataCleaningBusinesses.py`
    - `DataCleaningCrimeLevel.py`
    - ... (and other data cleaning scripts)
  - `UI/`: The user interface code for the web application.
- `venv/`: The directory for the virtual environment containing Python binaries and the installed packages.
- `requirements.txt`: Lists the Python dependencies for pip to install.

Run the application using the following command:
```bash
streamlit run UI/app.py
```

Make sure to navigate to the `UI` directory before running the command if your terminal is not already in that directory.

## Interactive Development with Jupyter in VSCode

For an enhanced interactive development experience, especially useful for running data cleaning and processing scripts, I recommend using the Jupyter extension for Visual Studio Code.

### Installation and Setup

1. If not already installed, download and install [Visual Studio Code](https://code.visualstudio.com/).
2. Inside VSCode, install the Jupyter extension by searching for it in the Extensions view (`Ctrl+Shift+X` or `Cmd+Shift+X` on macOS).
3. To enable sending code selections to the interactive Jupyter window:
   - Go to `File > Preferences > Settings` (or `Code > Preferences > Settings` on macOS).
   - Search for `Jupyter: Send Selection To Interactive Window`.
   - Ensure the checkbox for this setting is ticked.

### Running Data Cleaning Scripts

With the Jupyter extension installed and configured, you can easily run individual code cells of a `.py` file similar to how you would in a Jupyter Notebook.

- Open any of the data cleaning `.py` files located in the `src/data/` directory.
- Highlight the line of code and pressing `Shift+Enter`.

This setup streamlines the process of testing and running your data cleaning scripts, making it easier to iterate on your code.

Note: Ensure that your Python environment is activated and that all dependencies are installed for the scripts to run successfully.
