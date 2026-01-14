import pandas as pd
from django.db.models import Q

from ..models import Settlement
from ..utils import format_number, get_stats


class TotalStatsService:
    @staticmethod
    def get_top_regions():
        settlements = Settlement.objects.select_related(
            'municipality__region'
        ).values_list('municipality__region__name', 'municipality__name', 'population')

        df = pd.DataFrame(settlements, columns=['region', 'municipality', 'population'])

        grouped = df.groupby('region').agg({
            'population': 'sum',
            'municipality': 'nunique'
        })

        grouped['settlements'] = df.groupby('region').size()
        grouped = grouped.reset_index()
        grouped.columns = ['name', 'population', 'municipalities', 'settlements']
        grouped = grouped.sort_values('population', ascending=False)

        grouped['population'] = grouped['population'].apply(format_number)

        return grouped.to_dict('records')

    @staticmethod
    def get_population_stats():
        """Статистика по населению"""

        settlements = Settlement.objects.select_related(
            'municipality__region'
        ).values_list('municipality__region__name', 'population')

        df = pd.DataFrame(settlements, columns=['region', 'population'])

        region_pops = df.groupby('region')['population'].sum()

        return get_stats(region_pops)

    @staticmethod
    def get_population_stats_by_region(region_name):
        settlements = Settlement.objects.filter(municipality__region__name=region_name).select_related(
            'municipality__region'
        ).values_list('municipality__name', 'population')

        df = pd.DataFrame(settlements, columns=['municipality', 'population'])

        municipality_pops = df.groupby('municipality')['population'].sum()

        return get_stats(municipality_pops)

    @staticmethod
    def get_settlement_types_distribution(q_filter=None):
        """Распределение населения по типам поселений"""
        if not q_filter:
            q_filter = Q()

        settlements = Settlement.objects.filter(q_filter).values_list('type', 'population')

        df = pd.DataFrame(settlements, columns=['type', 'population'])

        stats = df.groupby('type')['population'].agg(['sum', 'count']).reset_index()
        stats.columns = ['type', 'population', 'count']

        stats = stats.sort_values('population', ascending=False)

        return stats.to_dict('records')

    @staticmethod
    def get_general_stats(region_name=None):
        """Общая статистика по регионам страны: регионы, муниципалитеты, поселения, пустые"""
        from ..models import Region, Municipality

        add_q_m = Q()
        add_q_s = Q()

        total_regions = Region.objects.count()

        regions_info = {'regions': total_regions}
        if region_name:
            add_q_m |= Q(region__name=region_name)
            add_q_s |= Q(municipality__region__name=region_name)
            regions_info = {}

        total_municipalities = Municipality.objects.filter(add_q_m).count()
        total_settlements = Settlement.objects.filter(add_q_s).count()

        empty_settlements = Settlement.objects.filter(add_q_s, population=0).count()

        return {
            **regions_info,
            'municipalities': total_municipalities,
            'settlements': total_settlements,
            'empty_settlements': empty_settlements,
            'populated_settlements': total_settlements - empty_settlements,
        }

    @staticmethod
    def get_population_distribution(q_filter=None):
        import json
        from settlements.models import Settlement

        population_distribution = list(
            Settlement.objects.filter(Q(population__gt=0) & (q_filter or Q())).values('population')
        )
        return json.dumps(population_distribution)