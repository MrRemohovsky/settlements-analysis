import pandas as pd


class DataProcessor:
    def aggregate_by_region(self, settlements_data):
        """Агрегировать данные по регионам"""
        df = pd.DataFrame(
            settlements_data,
            columns=['region', 'municipality', 'population']
        )

        grouped = df.groupby('region').agg({
            'population': 'sum',
            'municipality': 'nunique'
        })

        grouped['settlements'] = df.groupby('region').size()
        grouped = grouped.reset_index()
        grouped.columns = ['name', 'population', 'municipalities', 'settlements']

        return grouped.sort_values('population', ascending=False)

    def aggregate_by_municipality(self, settlements_data):
        """Агрегировать данные по муниципалитетам"""
        df = pd.DataFrame(
            settlements_data,
            columns=['municipality', 'population']
        )

        grouped = df.groupby('municipality').agg({
            'population': ['sum', 'count']
        })

        grouped.columns = ['population_total', 'settlements_count']
        grouped = grouped.reset_index()
        grouped = grouped[['municipality', 'settlements_count', 'population_total']]

        return grouped.sort_values('population_total', ascending=False)

    def calculate_statistics(self, data):
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], tuple):
                data = [item[0] if item[0] is not None else 0 for item in data]

        if not isinstance(data, pd.Series):
            data = pd.Series(data)

        data = data.dropna()
        data = data[data > 0]

        if len(data) == 0:
            return {
                'mean': 0,
                'median': 0,
                'max': 0,
                'min': 0,
                'total': 0
            }

        return {
            'mean': int(data.mean()),
            'median': int(data.median()),
            'max': int(data.max()),
            'min': int(data.min()),
            'total': int(data.sum())
        }

    def get_distribution_by_type(self, settlements_data):
        """Получить распределение поселений по типам"""
        df = pd.DataFrame(
            settlements_data,
            columns=['type', 'population']
        )

        stats = df.groupby('type')['population'].agg(['sum', 'count']).reset_index()
        stats.columns = ['type', 'population', 'count']

        return stats.sort_values('population', ascending=False)