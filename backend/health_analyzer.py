import uuid
from PIL import Image
import io
import numpy as np

class HealthAnalyzer:
    def __init__(self, chain, user_data):
        self.chain = chain
        self.user_data = user_data
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
            self.user_data.loc[self.user_data['user_id'] == user_id, 'health_record'] = data
            health_summary = self.chain.get_health_summary(data)
            self.user_data.loc[self.user_data['user_id'] == user_id, 'health_summary'] = health_summary
            self.user_data.to_csv('data/user_data.csv', index=False)
            return {
                "message": f"Health record for user {user_id} uploaded successfully",
                "health_summary": health_summary
            }
        except Exception as e:
            error_message = f"An error occurred while uploading health record: {str(e)}"
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
                'health_summary': ''
            }
            self.user_data.to_csv('data/user_data.csv', index=False)
            return {"user_id": user_id, "message": "User created successfully"}
        except Exception as e:
            error_message = f"An error occurred while creating the user: {str(e)}"
            print(error_message) 
            return {"error": error_message}

    def analyze_product(self, image_file, user_id=None):
        try:
            image = self.get_image(image_file)
            if image is None:
                return {"error": "Failed to open or process the image file"}
            
            return self.chain.process_nutrition_and_health(image, user_id)
        except Exception as e:
            error_message = f"An error occurred while analyzing the product: {str(e)} for user {user_id}"
            print(error_message) 
            return {"error": error_message}
