import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objs as go
import plotly.express as px
from utils.structs import ULD,Package,getCube
import csv
from heuristics.solver2_withSpaceDefrag import Solver2
import math
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def reset_state():
    """
    Resets the session state by removing specific keys if they exist.
    This function checks if 'uld_file' and 'package_file' keys are present 
    in the Streamlit session state and deletes them if they are found. 
    This can be useful for resetting the state of the application to a 
    clean slate, for example, when a user wants to start a new session 
    without any previously uploaded files.
    """

    if 'uld_file' in st.session_state:
        del st.session_state['uld_file']
    if 'package_file' in st.session_state:
        del st.session_state['package_file']
    # Use query parameters to force a page reload
    # st.query_params()

def page():
    """
    Renders the input page for uploading ULDs and Packages CSV files, providing guidelines for the expected file formats,
    and allowing users to proceed to the visualization page after successful uploads.
    The function includes:
    - A button to return to the main page.
    - Title and markdown description of the expected CSV file formats.
    - File uploaders for ULDs and Packages CSV files.
    - Display of additional information and options if both files are uploaded.
    - Sliders for selecting runtime and stability relaxation.
    - A button to proceed to the visualization page if both files are uploaded.
    - Warnings and information messages based on the file upload status.
    """
    
    # Add a button to return to main page
    if st.button("← Back to Main Page",key="back_to_main"):
        st.session_state.page = 'main'
        st.rerun()
        # st.experimental_rerun()

        
    # Title and description
    st.title("📦 ULDs and Packages CSV File Guidelines")
    st.markdown("""
    Upload your ULDs and Packages CSV files. Below are the expected formats for each file:

    ### *ULDs CSV* Format:
    - *ULD_id*: (string) Unique identifier for the ULD.
    - *Length*: (int/float) Length of the ULD.
    - *Width*: (int/float) Width of the ULD.
    - *Height*: (int/float) Height of the ULD.
    - *Weight_limit*: (float) Maximum weight limit of the ULD.

    ### *Packages CSV* Format:
    - *Package_id*: (string) Unique identifier for the package.
    - *Length*: (int/float) Length of the package.
    - *Width*: (int/float) Width of the package.
    - *Height*: (int/float) Height of the package.
    - *Weight*: (int/float) Weight of the package.
    - *Type*: (string) Package type ("Priority" or "Economy").
    - *Penalty*: (string/float) 
    - If "Type" is "Priority", this column must contain a "-".
    - If "Type" is "Economy", this column must contain a penalty value (float).
    
    Please make sure that the columns in your CSV files follow this structure and data type format for proper processing.
    """)

    # File uploaders
    col1, col2 = st.columns(2)
    with col1:
        uld_file = st.file_uploader("Upload ULDs CSV File", type=["csv"])
    with col2:
        package_file = st.file_uploader("Upload Packages CSV File", type=["csv"])
    
    
    # Display additional information if files are uploaded
    if uld_file and package_file:
        st.markdown("---")
        st.subheader("Upload Complete!")
        st.success("Files uploaded successfully!")
        st.session_state.uld_file = uld_file
        st.session_state.package_file = package_file
        userTimeout = st.slider("Select runtime (in minutes)", min_value=2, value=20, step = 2)
        st.session_state.timeout = userTimeout * 60
        # Add a button to proceed to visualization
        if st.button("Proceed to Visualization",key="proceed_to_visualization"):
            st.session_state.page = 'visualization'
            st.rerun()
    
           
    elif uld_file or package_file:
        st.warning("⚠ Please upload both files for processing.")
    else:
        st.info("ℹ Awaiting file uploads.")

    # if st.button("Reset"):
    #     reset_state()
    #     st.success("Files reset successfully!")

if __name__ == "__main__":
    page()
