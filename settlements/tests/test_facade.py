from django.test import TestCase
import pandas as pd

from settlements.facades import StatisticsFacade
from settlements.subsystems import DataProcessor


class DataProcessorUnitTestCase(TestCase):
    def test_aggregate_by_region_groups_data_correctly(self):
        """Проверяет агрегацию данных по регионам"""
        processor = DataProcessor()

        test_data = [
            ('Волгоград', 'Волгоград', 1000000),
            ('Волгоград', 'Камышин', 100000),
            ('Краснодар', 'Краснодар', 500000),
        ]

        result = processor.aggregate_by_region(test_data)

        # result это DataFrame с колонками: name, population, municipalities, settlements
        self.assertEqual(len(result), 2)  # 2 региона
        # Волгоград должен быть первым (больше население: 1100000 > 500000)
        self.assertEqual(result.iloc[0]['name'], 'Волгоград')
        self.assertEqual(result.iloc[0]['population'], 1100000)
        # Краснодар второй
        self.assertEqual(result.iloc[1]['name'], 'Краснодар')
        self.assertEqual(result.iloc[1]['population'], 500000)

    def test_calculate_statistics_with_real_data(self):
        """Проверяет расчёт статистики (mean, median, max, min, total)"""
        processor = DataProcessor()

        data = pd.Series([10, 20, 30, 40, 50])
        stats = processor.calculate_statistics(data)

        self.assertEqual(stats['mean'], 30)
        self.assertEqual(stats['median'], 30)
        self.assertEqual(stats['total'], 150)
        self.assertEqual(stats['max'], 50)
        self.assertEqual(stats['min'], 10)

    def test_calculate_statistics_with_empty_data(self):
        """Проверяет расчёт статистики для пустых данных"""
        processor = DataProcessor()

        data = pd.Series([], dtype=float)
        stats = processor.calculate_statistics(data)

        self.assertEqual(stats['mean'], 0)
        self.assertEqual(stats['median'], 0)
        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['max'], 0)
        self.assertEqual(stats['min'], 0)

    def test_processor_handles_large_numbers(self):
        """Проверяет обработку больших чисел"""
        processor = DataProcessor()

        data = pd.Series([1000000, 2000000, 3000000])
        stats = processor.calculate_statistics(data)

        self.assertEqual(stats['total'], 6000000)
        self.assertEqual(stats['mean'], 2000000)

    def test_aggregate_by_municipality_groups_correctly(self):
        """Проверяет агрегацию по муниципалитетам"""
        processor = DataProcessor()

        test_data = [
            ('Волгоград', 1000000),
            ('Волгоград', 500000),
            ('Камышин', 100000),
        ]

        result = processor.aggregate_by_municipality(test_data)

        self.assertEqual(len(result), 2)  # 2 муниципалитета
        # Волгоград первый (больше население)
        self.assertEqual(result.iloc[0]['municipality'], 'Волгоград')
        self.assertEqual(result.iloc[0]['population_total'], 1500000)


class FacadeSimpleUnitTestCase(TestCase):
    def test_facade_can_be_instantiated(self):
        facade = StatisticsFacade()
        self.assertIsNotNone(facade.fetcher)
        self.assertIsNotNone(facade.processor)
        self.assertIsNotNone(facade.formatter)

    def test_processor_integration(self):
        facade = StatisticsFacade()

        data = pd.Series([100, 200, 300])
        stats = facade.processor.calculate_statistics(data)

        self.assertEqual(stats['min'], 100)
        self.assertEqual(stats['max'], 300)
        self.assertEqual(stats['total'], 600)
        self.assertEqual(stats['median'], 200)
        self.assertEqual(stats['mean'], 200)