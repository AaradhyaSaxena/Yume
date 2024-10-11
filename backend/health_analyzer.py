import uuid
from PIL import Image
import io
import numpy as np
import base64
from io import BytesIO
import pandas as pd
import json
from langsmith import Client

client = Client()

class HealthAnalyzer:
    def __init__(self, chain, user_data):
        self.chain = chain
        self.user_data = user_data
        try:
            self.meals_data = pd.read_csv('data/meals_data.csv')
        except FileNotFoundError:
            self.meals_data = pd.DataFrame(columns=['user_id', 'protein', 'fats', 'carbohydrates', 'calorieConsumed', 'mealType'])
        pass

    def get_image(self, image_file):
        try:
            return Image.open(image_file)
        except IOError as e:
            print(f"Error opening image file: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error when opening image file: {e}")
            return None

    def get_user_health_summary(self, user_id):
        try:
            if user_id is None:
                return " "
            else:
                return self.user_data[self.user_data['user_id'] == user_id]['health_summary'].iloc[0]
        except IndexError:
            print(f"User with ID {user_id} not found")
            return " "
        except Exception as e:
            print(f"An error occurred while retrieving health summary: {str(e)}")
            return " "

    def upload_user_health_record(self, user_id, data):
        try:
            # print("health record: ", data)
            self.user_data.loc[self.user_data['user_id'] == user_id, 'health_record'] = data
            health_summary = self.chain.get_health_summary(data)
            print("health summary: ", health_summary.content)
            self.user_data.loc[self.user_data['user_id'] == user_id, 'health_summary'] = health_summary.content
            daily_intake = self.chain.get_daily_intake(data)
            print("daily intake: ", daily_intake.content)
            self.user_data.loc[self.user_data['user_id'] == user_id, 'target_nutrients'] = daily_intake.content 
            self.user_data.to_csv('data/user_data.csv', index=False)
            return {
                "message": f"Health record for user {user_id} uploaded successfully",
                "health_summary": health_summary.content,
                "target_nutrients": daily_intake.content
            }
        except Exception as e:
            error_message = f"An error occurred while uploading health record: {str(e)}"
            print(error_message) 
            return {"error": error_message}
        
    def add_user_preferences(self, user_id, preferences):
        print("user_id: ", user_id)
        print("preferences: ", preferences)
        try:
            self.user_data.loc[self.user_data['user_id'] == user_id, 'preferences'] = preferences
            self.user_data.to_csv('data/user_data.csv', index=False)
            return {"message": f"Preferences for user {user_id} added successfully"}
        except Exception as e:
            error_message = f"An error occurred while adding user preferences: {str(e)}"
            print(error_message)
            return {"error": error_message}

    def create_user(self, name, phone, email):
        try:
            user_id = str(uuid.uuid4())
            self.user_data.loc[len(self.user_data)] = {
                'user_id': user_id, 
                'name': name, 
                'phone': phone, 
                'email': email, 
                'health_record': '', 
                'health_summary': '',
                'preferences': '',
                'target_nutrients': ''
            }
            self.user_data.to_csv('data/user_data.csv', index=False)
            return {"user_id": user_id, "message": "User created successfully"}
        except Exception as e:
            error_message = f"An error occurred while creating the user: {str(e)}"
            print(error_message) 
            return {"error": error_message}
    
    def add_meal(self, user_id, result, mealType):
        try:
            meal_id = str(uuid.uuid4())
            self.meals_data.loc[len(self.meals_data)] = {
                'meal_id': meal_id,
                'user_id': user_id,
                'protein': result['protein'],
                'fats': result['fats'],
                'carbohydrates': result['carbohydrates'],
                'calorieConsumed': result['calories'],
                'mealType': mealType
            }
            self.meals_data.to_csv('data/meals_data.csv', index=False)
            return {"meal_id": user_id, "message": "Meal added successfully"}
        except Exception as e:
            error_message = f"An error occurred while adding the meal: {str(e)}"
            print(error_message)
            return {"error": error_message}

    def analyze_product(self, image_file, user_id=None):
        meals_summary = self.get_meals_summary_by_user(user_id)
        reccomendations, nutritional_info  = self.chain.process_nutrition_and_health(image_file, user_id, meals_summary)
        return {"result": reccomendations, "nutritional_info": nutritional_info}

    def calculate_exercise(self, calories=None):
        return self.chain.calculate_exercise(calories)
    
    def calculate_calories(self, image_file, user_id=None, meal_type=None):
        result = self.chain.calculate_calories(image_file, user_id)
        result = json.loads(result)
        result_dict = {
            "calories": result["calories"],
            "protein": result["protein"],
            "carbohydrates": result["carbohydrates"],
            "fats": result["fats"]
        }
        self.add_meal(user_id, result_dict, meal_type)
        return {"result": result_dict}
  
    def get_meals_summary_by_user(self, user_id):
        try:
            # Filter the meals_data by the provided user_id
            user_meals = self.meals_data[self.meals_data['user_id'] == user_id].copy()
            
            if user_meals.empty:
                return {"message": "No meals found for this user"}

            # Convert columns to numeric
            numeric_columns = ['protein', 'fats', 'carbohydrates', 'calorieConsumed']
            user_meals[numeric_columns] = user_meals[numeric_columns].apply(pd.to_numeric, errors='coerce')
            totals = user_meals[numeric_columns].sum()

            print("total_calories", totals['calorieConsumed'])

            return {
                "total_protein": totals['protein'],
                "total_fats": totals['fats'],
                "total_carbohydrates": totals['carbohydrates'],
                "total_calories": totals['calorieConsumed']
                }
        except Exception as e:
            error_message = f"An error occurred while retrieving meal summary: {str(e)}"
            print(error_message)
            return {"error": error_message}
    