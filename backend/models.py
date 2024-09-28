from langchain_core.pydantic_v1 import BaseModel

class NutritionalInfo(BaseModel):
    calories: int
    total_fat: float
    saturated_fat: float
    trans_fat: float
    cholesterol: int
    sodium: int
    total_carbohydrate: int
    dietary_fiber: int
    total_sugars: int
    protein: int
    # Add any other nutritional fields you want to extract

class HealthRecommendation(BaseModel):
    is_suitable: bool
    recommendation: str
    explanation: str