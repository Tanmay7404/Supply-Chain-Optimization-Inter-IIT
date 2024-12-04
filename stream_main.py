import streamlit as st
import page1
import page2
import page3


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
                # st.experimental_rerun()
            elif input_mode == "Manual Input":
                st.session_state.page = "manual_input"
                # st.experimental_rerun()
    st.caption("Double click to proceed")


def main():
    # Page rendering based on session state
    if st.session_state.page == 'main':
        main_page()
    elif st.session_state.page == 'upload_file':
        page1.page()
    elif st.session_state.page == 'manual_input':
        page2.page()
    elif st.session_state.page == 'visualization':
        page3.page()

if __name__ == "__main__":
    main()