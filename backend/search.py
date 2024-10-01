import pandas as pd
from flask import jsonify

class KeywordSearch:
    def __init__(self):
        self.df = pd.read_csv("data/common_food.csv")

    def search(self, keyword, columns=['Food']):
        """
        Search for a keyword in the specified columns of the DataFrame.
        """
        if columns is None:
            columns = self.df.columns

        mask = self.df[columns].apply(lambda x: x.astype(str).str.contains(keyword, case=False)).any(axis=1)

        result = self.df[mask]
        if not result.empty:
            return jsonify(result.to_dict(orient='records'))
        else:
            return jsonify({'error': 'Food not found'}), 404

    def multi_keyword_search(self, keywords, columns=['Food'], match_all=False):
        """
        Search for multiple keywords in the specified columns of the DataFrame.
        If no columns are specified, search in all columns.

        :param keywords: list of str, the keywords to search for
        :param columns: list of str, the columns to search in (optional)
        :param match_all: bool, if True, all keywords must be present (default: False)
        :return: pandas DataFrame, rows containing the keywords
        """
        if columns is None:
            columns = self.df.columns

        masks = []
        for keyword in keywords:
            mask = self.df[columns].apply(lambda x: x.astype(str).str.contains(keyword, case=False)).any(axis=1)
            masks.append(mask)

        if match_all:
            final_mask = pd.concat(masks, axis=1).all(axis=1)
        else:
            final_mask = pd.concat(masks, axis=1).any(axis=1)

        result = self.df[final_mask]
        if not result.empty:
            return jsonify(result.to_dict(orient='records'))
        else:
            return jsonify({'error': 'Food not found'}), 404