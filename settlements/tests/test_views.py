from django.test import TestCase, Client
from settlements.models import Region, Municipality, Settlement


class StatsViewIntegrationTestCase(TestCase):
    """Интеграционные тесты главной страницы со статистикой"""

    @classmethod
    def setUpTestData(cls):
        cls.region1 = Region.objects.create(
            name='Волгоградская область'
        )
        cls.region2 = Region.objects.create(
            name='Краснодарский край'
        )

        # Создаём муниципалитеты
        cls.mun1 = Municipality.objects.create(
            name='Волгоград',
            region=cls.region1
        )
        cls.mun2 = Municipality.objects.create(
            name='Камышин',
            region=cls.region1
        )
        cls.mun3 = Municipality.objects.create(
            name='Краснодар',
            region=cls.region2
        )

        Settlement.objects.create(
            name='Волгоград',
            municipality=cls.mun1,
            type='город',
            population=1000000
        )
        Settlement.objects.create(
            name='Камышин',
            municipality=cls.mun2,
            type='город',
            population=100000
        )
        Settlement.objects.create(
            name='Краснодар',
            municipality=cls.mun3,
            type='город',
            population=500000
        )

    def setUp(self):
        self.client = Client()

    def test_stats_view_returns_200(self):
        """Проверяет что главная страница возвращает статус 200"""
        response = self.client.get('/settlements/')
        self.assertEqual(response.status_code, 200)

    def test_stats_view_contains_top_regions(self):
        """Проверяет что в контексте есть регионы"""
        response = self.client.get('/settlements/')
        self.assertIn('top_regions', response.context)
        # Должны быть регионы
        self.assertGreater(len(response.context['top_regions']), 0)

    def test_stats_view_contains_general_stats(self):
        """Проверяет что в контексте есть общая статистика"""
        response = self.client.get('/settlements/')
        self.assertIn('general_stats', response.context)

        stats = response.context['general_stats']
        self.assertIn('municipalities', stats)
        self.assertIn('settlements', stats)

    def test_stats_view_contains_population_stats(self):
        """Проверяет что в контексте есть статистика населения"""
        response = self.client.get('/settlements/')
        self.assertIn('population_stats', response.context)

        stats = response.context['population_stats']
        self.assertIn('mean', stats)
        self.assertIn('median', stats)
        self.assertIn('total', stats)

    def test_stats_view_contains_settlement_types(self):
        """Проверяет что в контексте есть распределение по типам"""
        response = self.client.get('/settlements/')
        self.assertIn('settlement_types', response.context)
        self.assertGreater(len(response.context['settlement_types']), 0)

    def test_stats_view_contains_breadcrumb(self):
        """Проверяет что в контексте есть хлебные крошки"""
        response = self.client.get('/settlements/')
        self.assertIn('breadcrumb', response.context)


class RegionDetailViewIntegrationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.region = Region.objects.create(
            name='Волгоградская область'
        )

        cls.mun1 = Municipality.objects.create(
            name='Волгоград',
            region=cls.region
        )
        cls.mun2 = Municipality.objects.create(
            name='Камышин',
            region=cls.region
        )

        Settlement.objects.create(
            name='Волгоград',
            municipality=cls.mun1,
            type='город',
            population=1000000
        )
        Settlement.objects.create(
            name='Старая Полтавка',
            municipality=cls.mun1,
            type='село',
            population=5000
        )
        Settlement.objects.create(
            name='Камышин',
            municipality=cls.mun2,
            type='город',
            population=100000
        )

    def setUp(self):
        self.client = Client()

    def test_region_view_returns_200(self):
        """Проверяет что страница региона возвращает 200"""
        region_name = 'Волгоградская область'
        url = f'/settlements/regions/{region_name}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_region_view_displays_region_name(self):
        """Проверяет что регион отображается в контексте"""
        region_name = 'Волгоградская область'
        url = f'/settlements/regions/{region_name}/'
        response = self.client.get(url)
        self.assertIn('region_name', response.context)
        self.assertEqual(response.context['region_name'], region_name)

    def test_region_view_lists_municipalities(self):
        """Проверяет что муниципалитеты отображаются"""
        region_name = 'Волгоградская область'
        url = f'/settlements/regions/{region_name}/'
        response = self.client.get(url)
        self.assertIn('municipalities', response.context)

        municipalities = response.context['municipalities']
        self.assertEqual(len(municipalities), 2)

    def test_region_view_shows_region_stats(self):
        """Проверяет что статистика региона выводится"""
        region_name = 'Волгоградская область'
        url = f'/settlements/regions/{region_name}/'
        response = self.client.get(url)

        self.assertIn('population_stats', response.context)
        self.assertIn('region_stats', response.context)

    def test_region_view_contains_settlement_types_chart(self):
        """Проверяет что в контексте есть распределение типов"""
        region_name = 'Волгоградская область'
        url = f'/settlements/regions/{region_name}/'
        response = self.client.get(url)

        self.assertIn('settlement_types_chart', response.context)


class MunicipalityDetailViewIntegrationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.region = Region.objects.create(
            name='Волгоградская область'
        )

        cls.municipality = Municipality.objects.create(
            name='Волгоград',
            region=cls.region
        )

        cls.settlement1 = Settlement.objects.create(
            name='Волгоград',
            municipality=cls.municipality,
            type='город',
            population=1000000
        )
        cls.settlement2 = Settlement.objects.create(
            name='Старая Полтавка',
            municipality=cls.municipality,
            type='село',
            population=5000
        )
        cls.settlement3 = Settlement.objects.create(
            name='Заячья Балка',
            municipality=cls.municipality,
            type='посёлок',
            population=2000
        )

    def setUp(self):
        self.client = Client()

    def test_municipality_view_returns_200(self):
        """Проверяет статус 200 для страницы муниципалитета"""
        region_name = 'Волгоградская область'
        municipality_name = 'Волгоград'
        url = f'/settlements/regions/{region_name}/{municipality_name}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_municipality_view_shows_settlements(self):
        """Проверяет что поселения выводятся"""
        region_name = 'Волгоградская область'
        municipality_name = 'Волгоград'
        url = f'/settlements/regions/{region_name}/{municipality_name}/'
        response = self.client.get(url)

        self.assertIn('page_obj', response.context)
        # page_obj содержит поселения (3 шт)
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_municipality_view_filter_by_type(self):
        """Проверяет фильтрацию поселений по типам"""
        region_name = 'Волгоградская область'
        municipality_name = 'Волгоград'
        url = f'/settlements/regions/{region_name}/{municipality_name}/?type=город'
        response = self.client.get(url)

        page_obj = response.context['page_obj']
        # Должно остаться только 1 (город)
        self.assertEqual(len(page_obj), 1)
        self.assertEqual(page_obj[0]['type'], 'город')

    def test_municipality_view_search_settlements(self):
        """Проверяет поиск по названию поселения"""
        region_name = 'Волгоградская область'
        municipality_name = 'Волгоград'
        url = f'/settlements/regions/{region_name}/{municipality_name}/?search=Старая'
        response = self.client.get(url)

        page_obj = response.context['page_obj']
        # Должно найтись только 1 (Старая Полтавка)
        self.assertEqual(len(page_obj), 1)
        self.assertIn('Старая', page_obj[0]['name'])

    def test_municipality_view_shows_statistics(self):
        """Проверяет что статистика муниципалитета выводится"""
        region_name = 'Волгоградская область'
        municipality_name = 'Волгоград'
        url = f'/settlements/regions/{region_name}/{municipality_name}/'
        response = self.client.get(url)

        self.assertIn('population_stats', response.context)
        self.assertIn('general_stats', response.context)

    def test_municipality_view_shows_settlement_types(self):
        """Проверяет что выводятся типы поселений"""
        region_name = 'Волгоградская область'
        municipality_name = 'Волгоград'
        url = f'/settlements/regions/{region_name}/{municipality_name}/'
        response = self.client.get(url)

        self.assertIn('settlement_types', response.context)
        # Должны быть 3 типа
        self.assertEqual(len(response.context['settlement_types']), 3)

    def test_municipality_view_pagination(self):
        """Проверяет что работает пагинация"""
        region_name = 'Волгоградская область'
        municipality_name = 'Волгоград'
        url = f'/settlements/regions/{region_name}/{municipality_name}/'
        response = self.client.get(url)

        self.assertIn('page_obj', response.context)
        self.assertIn('total_results', response.context)
        self.assertEqual(response.context['total_results'], 3)