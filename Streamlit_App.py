import streamlit as st
import streamlitPages.Input as Input
import streamlitPages.Manual_Input as Manual_Input
import streamlitPages.Visualisation as Visualisation


# Initialize session state for page navigation if not already set
if 'page' not in st.session_state:
    st.session_state.page = 'main'

def main_page():
    st.title("ULDs and Packages - Input Selection")
    st.markdown("""
    Choose how you want to provide data for ULDS and Packages:
    - **Upload File**: Upload CSV files with predefined formats.
    - **Manual Input**: Add details manually using forms and sliders.
    """)
    
    input_mode = st.radio("Select Input Mode", ["Upload File", "Manual Input"], index=0)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Proceed"):
            if input_mode == "Upload File":
                st.session_state.page = "upload_file"
                st.rerun()
            elif input_mode == "Manual Input":
                st.session_state.page = "manual_input"
                st.rerun()
    


def main():
    # Page rendering based on session state
    if st.session_state.page == 'main':
        main_page()
    elif st.session_state.page == 'upload_file':
        Input.page()
    elif st.session_state.page == 'manual_input':
        Manual_Input.page()
    elif st.session_state.page == 'visualization':
        Visualisation.page()

if __name__ == "__main__":
    main()