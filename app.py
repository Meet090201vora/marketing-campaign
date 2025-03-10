import streamlit as st
import os
import json
import time
from prompt import system_prompt, system_prompt_theme_replacer
from dotenv import load_dotenv
import requests
from config import *
from openai import OpenAI
from utils import get_image_base64, image_summarizer
from PIL import Image

# custom layout for the app in size
st.set_page_config(layout="wide", page_title="Email Marketing App")
st.sidebar.title("")

# OpenAI API Client
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Ensure temp directory exists
os.makedirs("temp", exist_ok=True)

# Initialize session state for uploaded file
if "uploaded_file_path" not in st.session_state:
    st.session_state.uploaded_file_path = None

# Function to save uploaded file immediately
def save_uploaded_file(uploaded_file):
    """Save the uploaded image and store its path in session state."""
    if uploaded_file:
        unique_id = str(int(time.time()))  # Unique identifier for temp storage
        temp_image_path = f"temp/{unique_id}_image.jpg"

        with open(temp_image_path, "wb") as f:
            f.write(uploaded_file.read())

        st.session_state.uploaded_file_path = temp_image_path  # Store in session state
        st.session_state.file_uploaded = True
        return temp_image_path
    return None

# Process Image
def process_image_input(input_email, image_path):
    """Process the uploaded image and return its summary."""
    status_encoding_img, encoded_image = get_image_base64(image_path)
    if not status_encoding_img:
        return False, "Error while converting image to encoded string"

    status_img_sum, text = image_summarizer(input_email, encoded_image, url_flag=False)
    if not status_img_sum:
        return False, "Error while summarizing the image content."
    
    markdown_text = text.replace("```markdown", "").replace("```", "")
    system_prompt_theme_replacer_copy = system_prompt_theme_replacer.replace("<email_content>", input_email).replace("<markdown_template>", markdown_text)

    try:
        messages_dummy = [{"role": "system", "content": system_prompt_theme_replacer_copy}]
        response = client.chat.completions.create(
            model="gpt-4.5-preview",
            messages=messages_dummy,
            temperature=0.01,
            max_tokens=4000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            seed=0,
        )

        raw_text = response.choices[0].message.content
        json_output = raw_text.replace("```markdown", "").replace("```", "")
        return True, json_output
    except Exception as e:
        return False, f"Error: {e}"


def generate_content(brand, formula, tags, discount, goal, brief_description, points_to_cover, brand_service_target, campaign_angle, campaign_category):
    """Generate marketing content based on user inputs."""
    formula_description = copyright_formulaes.get(formula, {}).get(
        "description", "NOT APPLICABLE"
    )
    brand_info = brand_descriptions.get(brand.lower(), "No specific brand information available.")
    tags_str = ", ".join(tags) if tags else "NOT APPLICABLE"
    discount_str = f"{discount}% off" if discount and discount != 0 else "NOT APPLICABLE"
    brief_description = brief_description if brief_description else "NOT GIVEN"
    points_to_cover = points_to_cover if points_to_cover else "NOT GIVEN"
    brand_service_target = brand_service_target if brand_service_target else "General brand offerings"
    goal = goal if goal else "General engagement and conversions"

    system_prompt_dynamic = system_prompt \
        .replace("<brand>", brand) \
        .replace("<formula_description>", formula_description) \
        .replace("<brand_info>", brand_info) \
        .replace("<tags_str>", tags_str) \
        .replace("<discount>", discount_str) \
        .replace("<goal>", goal) \
        .replace("<brief_description>", brief_description) \
        .replace("<points_to_cover>", points_to_cover) \
        .replace("<campaign_angle>", campaign_angle) \
        .replace("<campaign_category>", campaign_category) \
        .replace("<brand_service_target>", brand_service_target)

    try:
        messages_dummy = [{"role": "system", "content": system_prompt_dynamic}]
        response = client.chat.completions.create(
            model="gpt-4.5-preview",
            messages=messages_dummy,
            temperature=0.01,
            max_tokens=4000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            seed=0,
        )

        raw_text = response.choices[0].message.content
        json_output = raw_text.replace("```markdown", "").replace("```", "")
        return True, json_output
    except Exception as e:
        return False, str(e)


# Set custom styles
st.markdown(
    """
    <style>
    .title-container {
        display: flex;
        justify-content: center;
        align-items: center;
        font-size:35px;
        font-weight: bold;
        margin-bottom: 15px;

    }
    .title-container img {
        height: 40px;  # Adjust logo size here
        margin-left: 10px;
        margin-right: 10px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# HTML with centered title and logo
st.markdown(
    """
    <div class="title-container">
        <img src="https://unhyd.com/wp-content/uploads/2024/08/Skype_Picture_2024_02_10T05_09_31_787Z-1.png" alt="Logo" />
        <span>Email Marketing App</span>
    </div>
    """, 
    unsafe_allow_html=True
)

# Layout for input fields
col1, col2, col3 = st.columns([2, 2, 4])

with col1:
    selected_brand = st.selectbox("Select a brand:", ["Limitless", "Swole AF", "Watch Connect", "Glowup", "Regenics", "Capsule Shop"], index=0)

with col2:
    selected_formula = st.selectbox("Select a formula:", [None, "FAB", "PASTOR", "AIDA"], index=0)

with col3:
    selected_tags = st.multiselect("Select tags:", ["content", "education", "sale", "social proof", "promotion", "survey", "gamified"], default=["content"])

# Discount Slider
discount = st.slider("Select Discount Percentage:", min_value=0, max_value=100, value=5, step=1)

col11, col12, col13 = st.columns([4,2,2])
brand_service_target = ""
with col11:
    brand_service_target = st.text_input("Which brand service is the mail targeting?", placeholder="Unhyde has launched a new web design service for small buisnees owners.")

campaign_angle = "Promotional"
with col12:
    campaign_angle = st.selectbox("Select Campaign Angle", list(campaign_categories.keys()), index=0)

campaign_category = "Tips and Tricks"
with col13:
    campaign_category = st.selectbox("Select Campaign Category", campaign_categories[campaign_angle])


# User Inputs
goal = st.text_input("Goal of the email:", placeholder="Increase sales by 20%")
brief_description = st.text_area("Brief Description:", placeholder="A campaign to educate customers about our product's benefits.")
points_to_cover = st.text_area("Points to Cover:", placeholder="- Brand Info\n- Personal Message\n- Year Highlights\n- Customer Impact")

# Image Upload Section (Processed immediately)
# st.subheader("📷 Upload an Image for Analysis")
uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "png"])

# Store file as soon as it is uploaded
if uploaded_file:
    temp_image_path = save_uploaded_file(uploaded_file)
else:
    temp_image_path = st.session_state.uploaded_file_path  # Retrieve stored path if exists

with st.expander("Preview Before Generating"):
    st.write(f"**Brand:** {selected_brand}")
    st.write(f"**Target of Brand** {brand_service_target}")
    st.write(f"**Formula:** {selected_formula}")
    st.write(f"**Tags:** {', '.join(selected_tags)}")
    st.write(f"**Discount:** {discount}%")
    st.write(f"**Goal:** {goal}")
    st.write(f"**Brief Description:** {brief_description}")
    st.write(f"**Points to Cover:** {points_to_cover}")
    st.write(f"**Campaign Angle:** {campaign_angle}")
    st.write(f"**Campaign Category:** {campaign_category}")



# Generate Button
if st.button("Generate"):
    with st.spinner("Generating content... Please wait."):
        # time.sleep(2)  # Simulate processing time
        # status, result = True, "Hello"  # Placeholder, replace with actual call
        status, result = generate_content(selected_brand, selected_formula, selected_tags, discount, goal, brief_description, points_to_cover, brand_service_target, campaign_angle, campaign_category)

    col5, col6, col7 = st.columns([3, 2, 3])
    if status:
        # st.subheader("Generated Campaign Content")
        styled_result = f"""
        <div style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6;">
            {result}
        </div>
        """

        with col5:
            with st.expander("Email Draft"):
                st.markdown(result, unsafe_allow_html=True)
        #st.markdown(result)

        # Process Image if Available
        with col6:
            if temp_image_path:
                image = Image.open(temp_image_path)
                # Resize to 512x1024
                image = image.resize((350, 1000))
                st.image(image, caption="Uploaded Image", use_column_width=True)


        with col7:
            if temp_image_path:
                with st.spinner("Analyzing image content... Please wait."):
                    status, msg = process_image_input(result, temp_image_path)
                    if status:
                        with st.expander("Theme aligned Email"):
                            st.markdown(msg, unsafe_allow_html=True)
                        # delete the file of image
                        if os.path.exists(temp_image_path):
                            os.remove(temp_image_path)
                    else:
                        st.error("❌ Error in image processing.")
    else:
        st.error(f"❌ Error: {result}")
