import json

import pandas as pd


class DataFormatter:
    @staticmethod
    def format_number(num):
        """Форматировать число с разделителями (1 000 000)"""
        if num is None or pd.isna(num):
            return '0'

        return f"{int(num):,}".replace(',', ' ')

    def format_dataframe_column(self, dataframe, column='population'):
        """Форматировать колонку DataFrame"""
        dataframe[column] = dataframe[column].apply(
            lambda x: self.format_number(x) if pd.notna(x) else '0'
        )
        return dataframe

    def dataframe_to_dict_records(self, dataframe):
        """Преобразовать DataFrame в список словарей"""
        return dataframe.to_dict('records')

    def statistics_to_formatted_dict(self, stats):
        """Форматировать словарь со статистикой"""
        if not isinstance(stats, dict):
            return stats

        formatted = {}
        for key, value in stats.items():
            formatted[key] = self.format_number(value)

        return formatted

    def dict_to_json(self, data):
        """Преобразовать словарь в JSON для передачи на фронтенд"""
        return json.dumps(data)