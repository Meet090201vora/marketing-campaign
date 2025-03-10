import streamlit as st

# Set custom background color using CSS
st.markdown(
    """
    <style>
    body {
        background-color: purple;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Example content
st.title("Streamlit with Purple Background")
st.write("This is an example of a Streamlit app with a purple background.")
