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

    # Dropdown for selecting the meal type
    meal_type = st.selectbox("Select Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])

    # File uploader for the meal image
    uploaded_meal_image = st.file_uploader("Upload an image of your meal", type=["jpg", "png", "jpeg"])

    # Submit button for calorie intake analysis
    if st.button("Submit Meal for Calorie Analysis"):
        if uploaded_meal_image is None:
            st.error("Please upload an image of your meal.")
        elif not user_id_calorie:
            st.error("Please enter your User ID.")
        else:
            try:
                # Convert the uploaded meal image to bytes for sending to the API
                files = {
                    'meal_image': uploaded_meal_image.getvalue(),  # Meal image
                }
                data = {
                    'user_id': user_id_calorie,  # User ID
                    'meal_type': meal_type  # Meal type (Breakfast, Lunch, Dinner, Snacks)
                }

                # API URL (replace with the actual Flask API URL)
                api_url = "http://localhost:5001/analyze_meal"

                # Send the POST request to Flask API for calorie analysis
                response = requests.post(api_url, files={'meal_image': uploaded_meal_image}, data=data)

                # Handle the response
                if response.status_code == 200:
                    result = response.json()
                    st.write("### Calorie Analysis Result")
                    st.write(f"**Meal**: {result['meal_name']}")
                    st.write(f"**Meal Type**: {meal_type}")
                    st.write(f"**Total Calorie Intake**: {result['total_calories']} calories")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"An error occurred: {e}")
