from flask import Flask, request, jsonify
import os
import json
from health_analyzer import HealthAnalyzer
import uuid
import pandas as pd
class APP:
    def __init__(self, health_analyzer):
        self.app = Flask(__name__)
        self.health_analyzer = health_analyzer
        self.config = self.load_config()
        self.port = self.config.get('PORT', 5001)
        self.users_dict = self.init_users_dict()
        self.setup_routes()

    def load_config(self):
        with open('./config/config.json') as config_file:
            return json.load(config_file)
    
    def init_users_dict(self):
        df = pd.read_csv('./data/user_data.csv')
        # if df is empty, create a new row with default values
        if df.empty:
            df = pd.DataFrame({
                'user_id': [str(uuid.uuid4())],
                'name': ['Default User'],
                'phone': ['1234567890'],
                'email': ['default@example.com'],
                'health_record': ['']
            })
        return df.to_dict(orient='records')

    def setup_routes(self):
        @self.app.route('/status', methods=['GET'])
        def a_live():
            return "Alive!"

        @self.app.route('/analyze_product', methods=['POST'])
        def analyze_product():
            if 'image_file' not in request.files:
                return jsonify({"error": "No image file provided"}), 400

            image_file = request.files['image_file']  # File from frontend
            user_id = request.form.get('user_id')
       
            if not user_id:
                return jsonify({"error": "No user ID provided"}), 400

            # Directly pass the image file and user ID to analyze_product method
            analysis_result = self.health_analyzer.analyze_product(image_file, user_id)

            return jsonify(analysis_result)

        @self.app.route('/analyze_meal', methods=['POST'])
        def analyze_meal():
            if 'meal_image' not in request.files:
                return jsonify({"error": "No image file provided"}), 400

            image_file = request.files['meal_image']  # File from frontend
            user_id = request.form.get('user_id')

            if not user_id:
                return jsonify({"error": "No user ID provided"}), 400

            # Directly pass the image file and user ID to analyze_product method
            analysis_result = self.health_analyzer.analyze_meal(image_file, user_id)

            return jsonify(analysis_result)


        @self.app.route('/user_health/<string:user_id>', methods=['GET'])
        def get_user_health(user_id):
            health_summary = self.health_analyzer.get_user_health_summary(user_id)
            return jsonify(health_summary)

        # @self.app.route('/user_health/<string:user_id>', methods=['POST'])
        # def upload_user_health(user_id):
        #     data = request.json
        #     if not data:
        #         return jsonify({"error": "No health record data provided"}), 400
        #     result = self.health_analyzer.upload_user_health_record(user_id, data)
        #     return jsonify(result)

        @self.app.route('/user', methods=['POST'])
        def create_user():
            data = request.json
            if not data or 'name' not in data or 'phone' not in data:
                return jsonify({"error": "Name and phone number are required to create a user"}), 400
            
            name = data['name']
            phone = data['phone']
            email = data.get('email')  # Email is optional
            
            if phone in self.users_dict:
                return jsonify({"error": "User with this phone number already exists"}), 409
            
            user_id = str(uuid.uuid4())
            new_user = {
                'user_id': user_id,
                'name': name,
                'phone': phone,
                'email': email
            }
            
            self.users_dict[phone] = new_user
            self.health_analyzer.create_user(new_user)
            
            return jsonify(new_user)

    def run(self):
        self.app.run(port=self.port)