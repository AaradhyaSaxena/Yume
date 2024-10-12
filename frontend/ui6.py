import streamlit as st
import requests
from streamlit_lottie import st_lottie
import json

with open('config/config.json', 'r') as config_file:
    config = json.load(config_file)

BASE_URL = config['BASE_URL']

# Define custom styles for aesthetics
st.markdown(
    """
    <style>
    body {
        background-color: #f7f9fc;
        font-family: 'Poppins', sans-serif;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 8px 16px;
        font-size: 16px;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .stTextInput input {
        border: 1px solid #ccc;
        border-radius: 12px;
        padding: 10px;
        width: 100%;
    }
    .sidebar .sidebar-content {
        background-color: #F0F4F8;
    }
    </style>
    """, unsafe_allow_html=True
)

# Load Lottie animation
def load_lottie_file(filepath: str):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"An error occurred while loading the Lottie animation: {e}")
        return None

# Add sidebar navigation
def main():
    global BASE_URL

    st.sidebar.title("YuMe")
    
    st.sidebar.write("Welcome to the User Dashboard")
    user_id = st.sidebar.text_input("Enter your User ID")
    
    menu = ["Analyze Product", "User Profile", "Calorie Intake"]
    choice = st.sidebar.selectbox("Navigation", menu)

    # Move Lottie animation to the top of the main page instead of the sidebar
    col1, col2 = st.columns([1, 3])
    with col1:
        lottie_animation = load_lottie_file("frontend/animation/yumegrad.json")
        if lottie_animation:
            st_lottie(lottie_animation, height=150, width=200)
    with col2:
        st.title("YuMe")
        st.subheader("Guided by nutrition driven by you")

    # Navigate between tabs
    if choice == "Analyze Product":
        scan_tab(user_id)
    elif choice == "User Profile":
        dashboard_tab(user_id)
    elif choice == "Calorie Intake":
        calorie_intake_tab(user_id)

def scan_tab(user_id):
    st.header("Analyze Product & Burn Calories")
    
    uploaded_file = st.file_uploader("Upload an image for product analysis", type=["jpg", "png", "jpeg"])

    if st.button("Analyze Product"):
        if uploaded_file is None:
            st.error("Please upload an image.")
        elif not user_id:
            st.error("Please enter your User ID.")
        else:
            try:
                files = {
                    'image_file': uploaded_file.getvalue(),
                }
                data = {
                    'user_id': user_id
                }
                api_url = BASE_URL + "/analyze_product"
                response = requests.post(api_url, files=files, data=data)

                if response.status_code == 200:
                    result = response.json()

                    col1, col2 = st.columns([5, 3])

                    with col1:
                        st.subheader("Analysis Result")
                        st.markdown(result['result']['health_recommendation'])
                        st.image(uploaded_file, use_column_width='auto')

                    with col2:
                        burn_calories_from_excercises(result['result']['excercises_result'])

                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

def burn_calories_from_excercises(excercises_result):
    st.subheader("Burn Calories with Exercise")
    
    try:
        excercises_data = json.loads(excercises_result)
        cycling_lottie = load_lottie_file("frontend/animation/cycling.json")
        swimming_lottie = load_lottie_file("frontend/animation/swimming.json")
        running_lottie = load_lottie_file("frontend/animation/running.json")

        if 'cycling' in excercises_data:
            st.markdown(f"**Cycling**: {excercises_data['cycling']}")
            if cycling_lottie:
                st_lottie(cycling_lottie, height=150, width=150)

        if 'swimming' in excercises_data:
            st.markdown(f"**Swimming**: {excercises_data['swimming']}")
            if swimming_lottie:
                st_lottie(swimming_lottie, height=150, width=150)

        if 'running' in excercises_data:
            st.markdown(f"**Running**: {excercises_data['running']}")
            if running_lottie:
                st_lottie(running_lottie, height=150, width=150)

    except json.JSONDecodeError as e:
        st.error(f"Failed to parse exercises data: {e}")

def dashboard_tab(user_id):
    st.header("User Profile")
    
    uploaded_doc = st.file_uploader("Upload the health record document", type=["txt"])
    if st.button("Upload Health Record"):
        if uploaded_doc is None:
            st.error("Please upload the document.")
        elif not user_id:
            st.error("Please enter your User ID.")
        else:
            try:
                files = {
                    'file': ('health_record.txt', uploaded_doc.getvalue(), 'text/plain'),
                }
                data = {
                    'user_id': user_id
                }
                api_url = BASE_URL + "/health_record/"
                response = requests.post(api_url, files=files, data=data)

                if response.status_code == 200:
                    st.success(f"Document '{uploaded_doc.name}' uploaded successfully!")
                    st.markdown(uploaded_doc.getvalue().decode('utf-8'))
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    # Change the text input to a file uploader for PDF files
    uploaded_pdf = st.file_uploader("Upload your preferences document (PDF)", type=["pdf"])
    if st.button("Add Preferences"):
        if uploaded_pdf is None:
            st.error("Please upload your preferences document.")
        elif not user_id:
            st.error("Please enter your User ID.")
        else:
            try:
                files = {
                    'file': ('preferences.pdf', uploaded_pdf.getvalue(), 'application/pdf'),
                }
                data = {
                    'user_id': user_id
                }
                headers = {'Content-Type': 'application/pdf'}
                api_url = BASE_URL + "/health_sources/"
                response = requests.post(api_url, files=files, data=data)

                if response.status_code == 200:
                    st.success("Preferences document uploaded successfully!")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    user_preferences = st.text_input("Add Links to Trusted Sources")
    if st.button("Add Sources"):
        if user_preferences is None:
            st.error("Please enter your Links.")
        elif not user_id:
            st.error("Please enter your User ID.")
        else:
            try:
                data = {
                    'user_id': user_id,
                    'preferences': user_preferences
                }
                headers = {'Content-Type': 'application/json'}
                api_url = BASE_URL +"/preferences/"
                response = requests.post(api_url, json=data, headers=headers)

                if response.status_code == 200:
                    st.success(f"Preferences '{user_preferences}' added successfully!")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

def calorie_intake_tab(user_id):
    st.header("Calorie Intake Calculator")
    
    uploaded_file = st.file_uploader("Upload an image of your meal", type=["jpg", "png", "jpeg"])
    meal_type = st.selectbox("Select Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
    
    if st.button("Add Meal"):
        if uploaded_file is None:
            st.error("Please upload an image of your meal.")
        elif not user_id:
            st.error("Please enter your User ID.")
        else:
            try:
                files = {
                    'image_file': uploaded_file.getvalue(),
                }
                data = {
                    'user_id': user_id,
                    'meal_type': meal_type
                }
                api_url = BASE_URL + "/calculate_calories"
                response = requests.post(api_url, files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    st.subheader("Calorie Calculation Result")
                    st.markdown(result['result']['health_recommendation'])
                    st.image(uploaded_file)
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()