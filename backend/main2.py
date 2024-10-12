import os
import pandas as pd
from config import load_config
from chain import Chain
from health_analyzer import HealthAnalyzer
from vectorStore import VectorStore
from vectorStore2 import VectorStore2
from search import KeywordSearch
from app import APP

def main():
    load_config()

    pdf_path = "backend/best_foods.pdf"
    
    advisor = VectorStore(pdf_path, "shaun")
    advisor.add_to_stores()

    # Example query
    query = "what should I eat?"
    answer = advisor.query(query)
    print(f"Q: {query}\nA: {answer}")

    advisor2 = VectorStore2(pdf_path)
    #advisor2.add_to_stores()

     # Example query
    #query = "what should I eat in Breakfast?"
    #answer = advisor2.query(query)
    #print(f"Q: {query}\nA: {answer}")

    
    #df = pd.read_csv('data/user_data.csv')

    #llm_chain = Chain(df)
    #health_analyzer = HealthAnalyzer(llm_chain, df)
    #search = KeywordSearch()
    #app = APP(health_analyzer, search)
    
    #app.run()

if __name__ == '__main__':
    main()