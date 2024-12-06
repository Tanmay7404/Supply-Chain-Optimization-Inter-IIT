import streamlit as st
from utils.structs import ULD, Package


def reset_state():
    if 'manual_ulds' in st.session_state:
        del st.session_state.manual_ulds
    if 'manual_packages' in st.session_state:
        del st.session_state.manual_packages

def page():
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
    userTimeout = st.slider("Select runtime", min_value=1, value=20, step = 5)
    st.session_state.timeout = userTimeout
    if st.button("Proceed to Visualization",key="proceed_to_visualization"):
        st.session_state.page = 'visualization'
        st.rerun()

    if st.button("Reset"):
        reset_state()
        st.success("Inputs reset successfully!")
        st.rerun()

if __name__ == "__main__":
    page()