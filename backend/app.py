from flask import Flask, request, jsonify
import json
import pandas as pd
class APP:
    def __init__(self, health_analyzer, search):
        self.app = Flask(__name__)
        self.health_analyzer = health_analyzer
        self.search = search
        self.df = pd.read_csv('data/user_data.csv')
        self.config = self.load_config()
        self.port = self.config.get('PORT', 5005)
        self.setup_routes()

    def load_config(self):
        with open('./config/config.json') as config_file:
            return json.load(config_file)

    def setup_routes(self):
        @self.app.route('/status', methods=['GET'])
        def a_live():
            return "Alive!"

        ### Analyze Product: Return health recommendation
        @self.app.route('/analyze_product', methods=['POST'])
        def analyze_product():
            if 'image_file' not in request.files:
                return jsonify({"error": "No image file provided"}), 400

            image_file = request.files['image_file']
            user_id = request.form.get('user_id')

            if not user_id:
                return jsonify({"error": "No user ID provided"}), 400

            analysis_result = self.health_analyzer.analyze_product(image_file, user_id)
            nutritional_info = json.loads(analysis_result.get("nutritional_info"))
            
            calories = nutritional_info['calories_per_serving']
            calories = float(''.join(filter(str.isdigit, calories.split('.')[0])))
            
            exercises_result = self.health_analyzer.calculate_exercise(calories)

            serializable_result = {
                "result": {
                    "health_recommendation": analysis_result.get("result", "No recommendation available"),
                    "excercises_result": exercises_result
                }
                
            }
            return jsonify(serializable_result)


        ### Calculate Calories: Return nutrition information using image   
        @self.app.route('/calculate_calories', methods=['POST'])
        def calculate_calories():
            print("checking request.files", request.files)
            if 'image_file' not in request.files:
                print("No image file provided")
                return jsonify({"error": "No image file provided"}), 400

            image_file = request.files['image_file'] 
            user_id = request.form.get('user_id')
            meal_type = request.form.get('meal_type')

            if not user_id:
                print("No user ID provided")
                return jsonify({"error": "No user ID provided"}), 400

            analysis_result = self.health_analyzer.calculate_calories(image_file, user_id, meal_type)
            serializable_result = {
                "result": {
                    "health_recommendation": analysis_result.get("result", "No recommendation available")
                }
            }
            return jsonify(serializable_result)


        ### Get User Health Summary: Return health summary of the user  
        @self.app.route('/user_health/<string:user_id>', methods=['GET'])
        def get_user_health(user_id):
            health_summary = self.health_analyzer.get_user_health_summary(user_id)
            return jsonify(health_summary)

        ### Upload User Health Record: Upload the health record of the user  
        @self.app.route('/health_record/', methods=['POST'])
        def upload_user_health_record():
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400
            
            file = request.files['file']
            user_id = request.form.get('user_id')
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            
            if file and file.filename.endswith('.txt'):
                # Read the content of the text file
                file_content = file.read().decode('utf-8')
                
                # Pass the file content to the health analyzer
                result = self.health_analyzer.upload_user_health_record(user_id, file_content)
                return jsonify(result)
            else:
                return jsonify({"error": "Invalid file format. Please upload a .txt file"}), 400
        
         ### Upload User Health Record: Upload the health record of the user  
        @self.app.route('/health_sources/', methods=['POST'])
        def upload_user_health_sources():
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400
            
            file = request.files['file']
            user_id = request.form.get('user_id')
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            
            if file and file.filename.endswith('.pdf'):
                # Read the content of the PDF file
                file_content = file.read()  # You may need to process the PDF content as needed
                
                # Pass the file content to the health analyzer (assuming a method exists for this)
                result = self.health_analyzer.upload_user_health_sources(user_id, file_content)
                return jsonify(result)
            else:
                return jsonify({"error": "Invalid file format. Please upload a .pdf file"}), 400

        ### Create User: Create a new user  
        @self.app.route('/user', methods=['POST'])
        def create_user():
            data = request.json
            if not data or 'name' not in data or 'phone' not in data:
                return jsonify({"error": "Name and phone number are required to create a user"}), 400
            
            name = data['name']
            phone = data['phone']
            email = data.get('email')  # Email is optional
            
            if not self.df[self.df['phone'] == phone].empty:
                return jsonify({"error": "User with this phone number already exists"}), 409
            new_user = self.health_analyzer.create_user(name, phone, email)
            return jsonify(new_user)
        
        ### Search: Search for a keyword in the specified columns of the DataFrame      
        @self.app.route('/search', methods=['GET'])
        def search():
            keyword = request.args.get('keyword')
            columns = request.args.get('columns', ['Food'])
            result = self.search.search(keyword, columns)
            return result
        
        ### Add User Preferences: vegan, keto, etc.
        @self.app.route('/preferences/', methods=['POST'])
        def add_user_preferences():
            data = request.json
            if not data or 'user_id' not in data or 'preferences' not in data:
                return jsonify({"error": "User ID and preferences are required to add user preferences"}), 400
            
            user_id = data['user_id']
            preferences = data['preferences']   
            result = self.health_analyzer.add_user_preferences(user_id, preferences)
            return jsonify(result)
            

    def run(self):
        self.app.run(port=self.port)