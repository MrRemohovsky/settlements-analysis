import pandas as pd
from ..models import Settlement
from ..utils import format_number, get_stats


class MunicipalityStatsService:
    @staticmethod
    def get_municipalities_by_region(region_name):
        settlements = Settlement.objects.filter(
            municipality__region__name=region_name
        ).select_related('municipality').values_list(
            'municipality__name',
            'population'
        )

        df = pd.DataFrame(settlements, columns=['municipality', 'population'])

        grouped = df.groupby('municipality').agg({
            'population': ['sum', 'count']
        })

        grouped.columns = ['population_total', 'settlements_count']
        grouped = grouped.reset_index()
        grouped = grouped[['municipality', 'settlements_count', 'population_total']]

        grouped = grouped.sort_values('population_total', ascending=False)

        grouped['population_total'] = grouped['population_total'].apply(
            lambda x: format_number(int(x)) if pd.notna(x) else '0'
        )

        municipalities_data = grouped.to_dict('records')

        return municipalities_data

    @staticmethod
    def get_municipality_general_stats(region_name, municipality_name):
        settlements = Settlement.objects.filter(
            municipality__name=municipality_name,
            municipality__region__name=region_name
        )

        total_settlements = settlements.count()
        populated_settlements = settlements.filter(population__gt=0).count()
        empty_settlements = total_settlements - populated_settlements
        return {
            'settlements': total_settlements,
            'empty_settlements': empty_settlements,
            'populated_settlements': total_settlements - empty_settlements,
        }

    @staticmethod
    def get_municipality_population_stats(region_name, municipality_name):
        settlements = Settlement.objects.filter(
            municipality__name=municipality_name,
            municipality__region__name=region_name
        ).values_list('population')

        df = pd.DataFrame(settlements, columns=['population'])

        return get_stats(df)

    @staticmethod
    def get_municipality_settlements(region_name, municipality_name, search_query=None, settlement_type=None):
        """Получить поселения муниципалитета с фильтрацией и поиском"""

        settlements = Settlement.objects.filter(
            municipality__name=municipality_name,
            municipality__region__name=region_name
        ).select_related('municipality')

        if settlement_type:
            settlements = settlements.filter(type=settlement_type)

        if search_query:
            settlements = settlements.filter(name__icontains=search_query)

        settlements = settlements.order_by('-population')

        data = list(settlements.values('name', 'type', 'population'))

        return data

    @staticmethod
    def get_settlement_types(region_name, municipality_name):
        """Получить все типы поселений в муниципалитете"""

        types = Settlement.objects.filter(
            municipality__name=municipality_name,
            municipality__region__name=region_name
        ).values_list('type', flat=True).distinct().order_by('type')

        return list(types)