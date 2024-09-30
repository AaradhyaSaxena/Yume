import streamlit as st
import requests
from PIL import Image

# Sidebar for navigation
page = st.sidebar.radio("Select Page", ["Product Analysis", "Calorie Intake"])

# Product Analysis page
if page == "Product Analysis":
    # Title of the app
    st.title("Product Analysis")

    # Text input for the user ID
    user_id = st.text_input("Enter your User ID")

    # File uploader for the image
    uploaded_file = st.file_uploader("Upload an image for product analysis", type=["jpg", "png", "jpeg"])

    # Button to submit
    if st.button("Analyze Product"):
        if uploaded_file is None:
            st.error("Please upload an image.")
        elif not user_id:
            st.error("Please enter your User ID.")
        else:
            try:
                # Convert the uploaded file to bytes for sending to the API
                files = {
                    'image_file': uploaded_file.getvalue(),  # Image file
                }
                data = {
                    'user_id': user_id  # User ID
                }
                
                # API URL (replace with the actual Flask API URL)
                api_url = "http://localhost:5001/analyze_product"

                # Send the POST request to Flask API
                response = requests.post(api_url, files={'image_file': uploaded_file}, data={'user_id': user_id})

                # Handle the response
                if response.status_code == 200:
                    result = response.json()
                    st.write("### Analysis Result")
                    st.markdown(result['result']['health_recommendation'])
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"An error occurred: {e}")

# Calorie Intake page
elif page == "Calorie Intake":
    st.title("Calorie Intake Tracker")

    # Text input for the user ID
    user_id_calorie = st.text_input("Enter your User ID for Calorie Intake")

    # Input fields for calorie intake
    breakfast_calories = st.number_input("Enter Breakfast Calories", min_value=0)
    lunch_calories = st.number_input("Enter Lunch Calories", min_value=0)
    dinner_calories = st.number_input("Enter Dinner Calories", min_value=0)

    # Submit button for calorie intake
    if st.button("Submit Calorie Intake"):
        if not user_id_calorie:
            st.error("Please enter your User ID.")
        else:
            # Display the calorie intake summary
            st.write("### Calorie Intake Summary")
            st.write(f"**Breakfast**: {breakfast_calories} calories")
            st.write(f"**Lunch**: {lunch_calories} calories")
            st.write(f"**Dinner**: {dinner_calories} calories")
            
            total_calories = breakfast_calories + lunch_calories + dinner_calories
            st.write(f"**Total Calorie Intake**: {total_calories} calories")
