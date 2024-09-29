from flask import Flask, request, jsonify
import os
import json
import pandas as pd
class APP:
    def __init__(self, df, health_analyzer):
        self.app = Flask(__name__)
        self.health_analyzer = health_analyzer
        self.df = df
        self.config = self.load_config()
        self.port = self.config.get('PORT', 5001)
        self.setup_routes()

    def load_config(self):
        with open('./config/config.json') as config_file:
            return json.load(config_file)
    
    def setup_routes(self):
        @self.app.route('/status', methods=['GET'])
        def a_live():
            return "Alive!"

        @self.app.route('/analyze_product', methods=['POST'])
        def analyze_product():
            data = request.json
            image_file = data.get('image_file')
            user_id = data.get('user_id')

            if not image_file:
                return jsonify({"error": "No image file provided"}), 400

            image_path = os.path.join('data', 'product_image', image_file)
            if not os.path.exists(image_path):
                return jsonify({"error": "Image file not found"}), 404

            analysis_result = self.health_analyzer.analyze_product(image_path, user_id)
            return jsonify(analysis_result)

        @self.app.route('/user_health/<string:user_id>', methods=['GET'])
        def get_user_health(user_id):
            health_summary = self.health_analyzer.get_user_health_summary(user_id)
            return jsonify(health_summary)

        @self.app.route('/user_health/<string:user_id>', methods=['POST'])
        def upload_user_health(user_id):
            data = request.json
            if not data:
                return jsonify({"error": "No health record data provided"}), 400
            result = self.health_analyzer.upload_user_health_record(user_id, data)
            return jsonify(result)

        @self.app.route('/user', methods=['POST'])
        def create_user():
            data = request.json
            if not data or 'name' not in data or 'phone' not in data:
                return jsonify({"error": "Name and phone number are required to create a user"}), 400
            
            name = data['name']
            phone = data['phone']
            email = data.get('email') 
            if not self.df[self.df['phone'] == phone].empty:
                return jsonify({"error": "User with this phone number already exists"}), 409
            new_user = self.health_analyzer.create_user(name, phone, email)
            return jsonify(new_user)

    def run(self):
        self.app.run(port=self.port)