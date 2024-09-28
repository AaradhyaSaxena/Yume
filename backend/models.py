from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

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

class HealthRecommendation(BaseModel):
    is_suitable: bool
    recommendation: str
    explanation: str
    harmful_ingredients: List[str]
    allergens: List[str]
    misleading_info: List[str]

class HealthSummary(BaseModel):
    key_concerns: List[str] = Field(..., description="List of main health issues or conditions")
    dietary_restrictions: List[str] = Field(..., description="List of dietary restrictions")
    allergies: List[str] = Field(..., description="List of known allergies")
    additional_notes: str = Field("", description="Any additional relevant health information")
