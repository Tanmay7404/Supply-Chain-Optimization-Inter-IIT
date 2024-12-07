import streamlit as st
from utils.structs import ULD, Package


def reset_state():
    """
    Resets the session state by deleting 'manual_ulds' and 'manual_packages' 
    from the Streamlit session state if they exist.
    This function is useful for clearing any manually inputted data related 
    to ULDS (Unit Load Devices) and packages, ensuring that the session 
    state is clean and ready for new input.
    """

    if 'manual_ulds' in st.session_state:
        del st.session_state.manual_ulds
    if 'manual_packages' in st.session_state:
        del st.session_state.manual_packages

def page():
    """
    Renders the manual input page for ULDs and Packages in a Streamlit application.
    This function displays a form for users to manually input ULD (Unit Load Device) and Package details.
    It also provides options to return to the main page, reset inputs, and proceed to the visualization page.
    The inputs are stored in the Streamlit session state.
    The page includes the following sections:
    - Title: "Manual Input for ULDs and Packages"
    - Button to return to the main page
    - Initialization of session state for ULDs and Packages if not already present
    - ULD Input Section: Form to input ULD details (ID, Length, Width, Height, Weight Limit)
    - Package Input Section: Form to input Package details (ID, Length, Width, Height, Weight, Type, Penalty)
    - Display of current ULDs and Packages
    - Sliders to select runtime and stability relaxation
    - Button to proceed to the visualization page
    - Button to reset inputs
    Note:
    - The function assumes the existence of ULD and Package classes for creating ULD and Package objects.
    - The function uses Streamlit's session state to store and manage the inputs.
    """

    st.title("Manual Input for ULDs and Packages")
    
    # Add a button to return to main page
    if st.button("← Back to Main Page"):
        st.session_state.page = 'main'
        st.rerun()


    # Initialize session state for ULDs and Packages if not exists
    if 'manual_ulds' not in st.session_state:
        st.session_state.manual_ulds = []
    if 'manual_packages' not in st.session_state:
        st.session_state.manual_packages = []

    # ULD Input Section
    st.subheader("ULD Input")
    with st.form("uld_input_form"):
        uld_id = st.text_input("ULD ID")
        length = st.number_input("Length", min_value=0, step=1)
        width = st.number_input("Width", min_value=0, step=1)
        height = st.number_input("Height", min_value=0, step=1)
        weight_limit = st.number_input("Weight Limit", min_value=0, step=1)
        
        uld_submit = st.form_submit_button("Add ULD")
        if uld_submit:
            new_uld = ULD(str(length), str(width), str(height), str(weight_limit), uld_id)
            st.session_state.manual_ulds.append(new_uld)
            st.success(f"ULD {uld_id} added successfully!")

    # Package Input Section
    st.subheader("Package Input")
    with st.form("package_input_form"):
        package_id = st.text_input("Package ID")
        length = st.number_input("Length", min_value=0, step=1, key="pkg_length")
        width = st.number_input("Width", min_value=0, step=1, key="pkg_width")
        height = st.number_input("Height", min_value=0, step=1, key="pkg_height")
        weight = st.number_input("Weight", min_value=0, step=1)
        package_type = st.selectbox("Package Type", ["Priority", "Economy"])
        penalty = st.text_input("Penalty (use '-' for Priority)")
        
        package_submit = st.form_submit_button("Add Package")
        if package_submit:
            if package_type == "Economy":
                new_package = Package(str(length), str(width), str(height), str(weight), package_id, package_type, penalty)
            else:
                new_package = Package(str(length), str(width), str(height), str(weight), package_id, package_type)
            st.session_state.manual_packages.append(new_package)
            st.success(f"Package {package_id} added successfully!")

    # Display current ULDs and Packages
    st.subheader("Current Inputs")
    col1, col2 = st.columns(2)
    with col1:
        st.write("ULDs:")
        for uld in st.session_state.manual_ulds:
            st.write(f"ID: {uld.id}, Dimensions: {uld.length}x{uld.width}x{uld.height}")
    
    with col2:
        st.write("Packages:")
        for pkg in st.session_state.manual_packages:
            st.write(f"ID: {pkg.id}, Dimensions: {pkg.length}x{pkg.width}x{pkg.height}")

    # Proceed to Visualization
    userTimeout = st.slider("Select runtime (in minutes)", min_value=2, value=20, step = 2)
    stabilityThrehold = st.slider("Select stability Relaxation", min_value=0.1, value=0.5, step = 0.1, max_value=1.0)
    st.session_state.timeout = userTimeout * 60
    st.session_state.stabilityThrehold = stabilityThrehold
    if st.button("Proceed to Visualization",key="proceed_to_visualization"):
        st.session_state.page = 'visualization'
        st.rerun()

    if st.button("Reset"):
        reset_state()
        st.success("Inputs reset successfully!")
        st.rerun()

if __name__ == "__main__":
    page()
