import json
from langchain_google_vertexai import ChatVertexAI
from langchain.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import PydanticOutputParser
from models import NutritionalInfo, HealthRecommendation, HealthSummary
from langchain_google_vertexai import VertexAI

class Chain:
    def __init__(self, df):
        self.df = df
        self.llm = ChatVertexAI(model="gemini-1.5-pro")
        self.vision_model = VertexAI(model_name="gemini-pro-vision")
        self.nutritional_parser = PydanticOutputParser(pydantic_object=NutritionalInfo)
        self.health_recommendation_parser = PydanticOutputParser(pydantic_object=HealthRecommendation)

    # Extract nutritional information from an image of a nutrition facts table
    def extract_nutritional_info(self, image):
        prompt = ChatPromptTemplate.from_template(
            "Extract all nutritional information from this image of a nutrition facts table. "
            "Provide the output in a structured format."
        )
        chain = prompt | self.vision_model | self.nutritional_parser
        return chain.invoke({"image": image})
    
    # Extract health summary from a health record
    def get_health_summary(self, health_record):
        prompt = ChatPromptTemplate.from_template(
            "Given the following health record, extract a concise summary of the patient's "
            "key health concerns, dietary restrictions, and allergies that are relevant for "
            "assessing food product suitability. Focus on information that could impact "
            "nutritional recommendations.\n\n"
            "Health Record: {health_record}\n\n"
            "Provide the output as a structured summary."
        )
        chain = prompt | self.llm | PydanticOutputParser(pydantic_object=HealthSummary)
        return chain.invoke({"health_record": health_record})

    # Assess the health compatibility of a product for a user 
    def assess_health_compatibility(self, health_summary, nutritional_info):
        prompt = ChatPromptTemplate.from_template(
            "Given the following health summary and nutritional information, "
            "assess whether the product is suitable for the user. "
            "Health Summary: {health_summary}\n"
            "Nutritional Information: {nutritional_info}\n"
            "Provide a recommendation for consumption and explanation, "
            "along with a list of harmful ingredients and allergens, and misleading information."
        )
        chain = prompt | self.llm | self.health_recommendation_parser
        return chain.invoke({
            "health_summary": health_summary.model_dump_json(),
            "nutritional_info": nutritional_info.model_dump_json()
        })

    def process_nutrition_and_health(self, image, user_id):
        nutritional_info = self.extract_nutritional_info(image)
        health_summary = self.df[self.df['user_id'] == user_id]['health_summary'].values[0]
        recommendation, misleading_info, harmful_ingredients, allergens = self.assess_health_compatibility(health_summary, nutritional_info)
        return {
            "nutritional_info": nutritional_info,
            "health_summary": health_summary,
            "health_recommendation": recommendation,
            "harmful_ingredients": harmful_ingredients,
            "allergens": allergens,
            "misleading_info": misleading_info,   
        }

