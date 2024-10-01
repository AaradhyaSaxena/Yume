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
            if 'image_file' not in request.files:
                return jsonify({"error": "No image file provided"}), 400

            image_file = request.files['image_file']  # File from frontend
            user_id = request.form.get('user_id')

            if not user_id:
                return jsonify({"error": "No user ID provided"}), 400

            # Directly pass the image file and user ID to analyze_product method
            analysis_result = self.health_analyzer.analyze_product(image_file, user_id)

            serializable_result = {
                "result": {
                    "health_recommendation": analysis_result.get("result", "No recommendation available")
                }
            }
            return jsonify(serializable_result)


        @self.app.route('/user_health/<string:user_id>', methods=['GET'])
        def get_user_health(user_id):
            health_summary = self.health_analyzer.get_user_health_summary(user_id)
            return jsonify(health_summary)


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
        
        @self.app.route('/search', methods=['GET'])
        def search():
            keyword = request.args.get('keyword')
            columns = request.args.get('columns', ['Food'])
            result = self.search.search(keyword, columns)
            return result

    def run(self):
        self.app.run(port=self.port)