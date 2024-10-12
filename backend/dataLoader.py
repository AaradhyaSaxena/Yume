import pandas as pd

class DataLoader:
    @staticmethod
    def load_data(file_path):
        df = pd.read_csv(file_path)
        df['images'] = df['images'].apply(eval)
        return df