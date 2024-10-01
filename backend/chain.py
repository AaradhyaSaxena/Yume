import json
from langchain_google_vertexai import ChatVertexAI
from langchain.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import PydanticOutputParser
from models import NutritionalInfo, HealthRecommendation, NutritionFacts
from langchain_google_vertexai import VertexAI
from langchain.schema import AIMessage 
from PIL import Image


class Chain:
    def __init__(self, df):
        self.df = df
        self.llm = ChatVertexAI(model="gemini-1.5-pro")
        self.vision_model = VertexAI(model_name="gemini-pro-vision")
        self.nutritional_parser = PydanticOutputParser(pydantic_object=NutritionFacts)
        self.health_recommendation_parser = PydanticOutputParser(pydantic_object=HealthRecommendation)

    def extract_nutritional_info(self, image):
        prompt = ChatPromptTemplate.from_template(
             "From the given image, try to find the nutritional information table and extract the nutritional information."
             "Image: {image}\n"
             "If you can't find the nutritional information table, just return a string saying 'No nutritional information found'."
             "Use the information from the image only, and don't make any assumptions, or add any information, or use any other sources."
             "Provide the output as a string."
         )
        
        chain = prompt | self.vision_model
        try:
            image_content = image.read()
            if not image_content:
                return "Error: Empty image file"
            return chain.invoke({"image": image_content})
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
    def extract_nutritional_info_meal(self, image):
        prompt = ChatPromptTemplate.from_template(
            "tell me what do you see in this image? Do you see any food items? "
            "Image is : {image}"
            "Provide the output as a string."
        )
        chain = prompt | self.vision_model 
        return chain.invoke({"image": image})

    def assess_health_compatibility(self, health_record, nutritional_info):
        prompt = ChatPromptTemplate.from_template(
            "Given the following health record and nutritional information, "
            "assess whether the product is suitable for the user. "
            "Health Record: {health_record}\n"
            "Nutritional Information: {nutritional_info}\n"
            "How processed and nutrient deficit is the product?"
            "Is it high in fats, sugar, sodium, calories?"
            "Are Harmful Ingredients present?"
            "Provide the output as a string."
        )
        chain = prompt | self.llm 
        return chain.invoke({
            "health_record": health_record,
            "nutritional_info": nutritional_info
        })

    def assess_pros_cons(self, nutritional_info):
        prompt = ChatPromptTemplate.from_template(
            "Given the following nutritional information, "
            "assess the pros and cons of the product. "
            "Nutritional Information: {nutritional_info}\n"
            "How processed and nutrient deficit is the product? "
            "Is it high in fats, sugar, sodium, calories? "
            "Are harmful ingredients present? "
            "If the product is highly processed, list the pros as almost negligible."
        )
        chain = prompt | self.llm
        return chain.invoke({"nutritional_info": nutritional_info})

    def process_nutrition_and_health(self, image, health_record):
        image_content = image.read()
        if not image_content:
            return "Error: No image provided saunnn "
        nutritional_info = self.extract_nutritional_info(image)
        print("checking reccomendations   ", nutritional_info)
        #recommendation = self.assess_health_compatibility(health_record, nutritional_info)
        recs = self.assess_pros_cons(nutritional_info)
        if isinstance(recs, AIMessage):
            recommendations_content = recs.content
        else:
            recommendations_content = recs 
        print("checking reccomendations   ", recommendations_content)
        return {
            "health_recommendation": recommendations_content
        }

    def process_nutrition_and_health_meal(self, image):
        if image.read() is None:
            return "Error: No image provided saunnn "
        meal_calorie_intake = self.extract_nutritional_info_meal(image)
        print("meal is :  ", meal_calorie_intake)
        return meal_calorie_intake
        
