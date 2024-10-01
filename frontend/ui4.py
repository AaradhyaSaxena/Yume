import streamlit as st
import requests
from PIL import Image
import os

def scan_tab(user_id):
    # Text input for the user ID
    # user_id = st.text_input("Enter your User ID")

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
                response = requests.post(api_url, files=files, data=data)

                # Handle the response
                if response.status_code == 200:
                    result = response.json()
                    st.write("### Analysis Result")
                    st.markdown(result['result']['health_recommendation'])
                    st.image(uploaded_file)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"An error occurred: {e}")

def dashboard_tab(user_id):
    st.write("Welcome to the User Dashboard")
    # st.write("Here you can upload other documents and view analytics.")
    
    # Placeholder for document upload
    # curr_user_id = st.text_input("Enter your User ID")
    uploaded_doc = st.file_uploader("Upload the health record document", type=["txt"])

    # Button to submit
    if st.button("Upload Health Record"):
        if uploaded_doc is None:
            st.error("Please upload the doc.")
        elif not user_id:
            st.error("Please enter your User ID.")
        else:
            try:
                # Convert the uploaded file to bytes for sending to the API
                files = {
                    'file': ('health_record.txt', uploaded_doc.getvalue(), 'text/plain'),
                }
                data = {
                    'user_id': user_id  # User ID
                }
                
                # API URL (replace with the actual Flask API URL)
                api_url = "http://localhost:5001/health_record/"

                # Send the POST request to Flask API
                response = requests.post(api_url, files=files, data=data)

                # Handle the response
                if response.status_code == 200:
                    # result = response.json()
                    st.success(f"Document '{uploaded_doc.name}' uploaded successfully!")
                    # st.json(result['message'])
                    st.text("Uploaded file content:")
                    st.markdown(uploaded_doc.getvalue().decode('utf-8'))
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"An error occurred: {e}")

def daily_goals_tab(user_id):
    st.write("Welcome to the Daily Goals")

def main():
    st.title("YuMe")
    
    user_id = st.text_input("Enter your User ID")

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Analyze Product", "User Profile", "Daily goals"])
    
    with tab1:
        scan_tab(user_id)
    
    with tab2:
        dashboard_tab(user_id)

    with tab3:
        daily_goals_tab(user_id)

if __name__ == "__main__":
    main()