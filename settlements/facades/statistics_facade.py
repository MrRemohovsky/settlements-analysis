import pandas as pd
from django.db.models import Q

from settlements.services import DataFetcher, DataProcessor, DataFormatter


class StatisticsFacade:
    """
    Предоставляет упрощённый единый интерфейс,
    состоящей из трёх компонентов:
    - DataFetcher (получение данных из БД)
    - DataProcessor (обработка данных с Pandas)
    - DataFormatter (форматирование для отображения)
    """

    def __init__(self):
        self.fetcher = DataFetcher()
        self.processor = DataProcessor()
        self.formatter = DataFormatter()

    # ==================== ОБЩАЯ СТАТИСТИКА ====================

    def get_top_regions(self):
        """
        Получить топ регионов по населению.
        """
        raw_data = self.fetcher.fetch_all_settlements_with_relations()

        aggregated = self.processor.aggregate_by_region(raw_data)

        formatted = self.formatter.format_dataframe_column(aggregated, 'population')

        return self.formatter.dataframe_to_dict_records(formatted)

    def get_population_stats(self):
        """
        Получить общую статистику по населению (mean, median, max, min, total).
        """
        raw_data = self.fetcher.fetch_all_settlements_with_relations()
        df = pd.DataFrame(raw_data, columns=['region', 'municipality', 'population'])

        # Получить население по регионам
        region_pops = df.groupby('region')['population'].sum()

        # Вычислить статистику
        stats = self.processor.calculate_statistics(region_pops)

        # Форматировать для отображения
        return self.formatter.statistics_to_formatted_dict(stats)

    def get_general_stats(self, region_name=None):
        """
        Получить общую статистику по регионам, муниципалитетам и поселениям.
        """
        from settlements.models import Region, Municipality

        add_q_m = Q()
        add_q_s = Q()

        total_regions = Region.objects.count()
        regions_info = {'regions': total_regions}

        if region_name:
            add_q_m |= Q(region__name=region_name)
            add_q_s |= Q(municipality__region__name=region_name)
            regions_info = {}

        total_municipalities = Municipality.objects.filter(add_q_m).count()

        # Получить статистику по поселениям
        settlement_stats = self.fetcher.fetch_settlement_statistics(region_name)

        return {
            **regions_info,
            'municipalities': total_municipalities,
            'settlements': settlement_stats['total'],
            'empty_settlements': settlement_stats['empty'],
            'populated_settlements': settlement_stats['populated'],
        }

    # ==================== СТАТИСТИКА ПО РЕГИОНАМ ====================

    def get_population_stats_by_region(self, region_name):
        """
        Получить статистику по населению конкретного региона.
        """
        raw_data = self.fetcher.fetch_settlements_by_region(region_name)
        df = pd.DataFrame(raw_data, columns=['municipality', 'population'])

        municipality_pops = df.groupby('municipality')['population'].sum()

        return self.processor.calculate_statistics(municipality_pops)

    def get_municipalities_by_region(self, region_name):
        """
        Получить все муниципалитеты региона со статистикой.
        """
        raw_data = self.fetcher.fetch_settlements_by_region(region_name)

        aggregated = self.processor.aggregate_by_municipality(raw_data)

        formatted = self.formatter.format_dataframe_column(aggregated, 'population_total')

        return self.formatter.dataframe_to_dict_records(formatted)

    def get_settlement_types_distribution(self, q_filter=None):
        """
        Получить распределение поселений по типам.
        """
        from settlements.models import Settlement

        if not q_filter:
            q_filter = Q()

        settlements = Settlement.objects.filter(q_filter).values_list('type', 'population')

        stats = self.processor.get_distribution_by_type(settlements)
        return self.formatter.dataframe_to_dict_records(stats)

    def get_population_distribution(self, q_filter=None):
        """
        Получить распределение населения (для графиков).
        """
        from settlements.models import Settlement

        if not q_filter:
            q_filter = Q()

        population_distribution = list(
            Settlement.objects.filter(
                Q(population__gt=0) & (q_filter or Q())
            ).values('population')
        )

        return self.formatter.dict_to_json(population_distribution)

    # ==================== СТАТИСТИКА ПО МУНИЦИПАЛИТЕТАМ ====================

    def get_municipality_general_stats(self, region_name, municipality_name):
        """
        Получить общую статистику по муниципалитету.
        """
        settlement_stats = self.fetcher.fetch_settlement_statistics(
            region_name=region_name,
            municipality_name=municipality_name
        )

        return {
            'settlements': settlement_stats['total'],
            'empty_settlements': settlement_stats['empty'],
            'populated_settlements': settlement_stats['populated'],
        }

    def get_municipality_population_stats(self, region_name, municipality_name):
        """
        Получить статистику по населению муниципалитета.
        """
        raw_data = self.fetcher.fetch_settlements_by_municipality(
            region_name,
            municipality_name
        )

        stats = self.processor.calculate_statistics(raw_data)
        return stats

    def get_municipality_settlements(self, region_name, municipality_name,
                                     search_query=None, settlement_type=None):
        """
        Получить список поселений муниципалитета с фильтрацией.
        """
        settlements = self.fetcher.fetch_settlement_details(
            region_name,
            municipality_name,
            search_query,
            settlement_type
        )

        return list(settlements.values('name', 'type', 'population'))

    def get_settlement_types(self, region_name, municipality_name):
        """
        Получить все типы поселений в муниципалитете.
        """
        return list(
            self.fetcher.fetch_settlement_types(region_name, municipality_name)
        )