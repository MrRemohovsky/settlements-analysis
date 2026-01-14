from settlements.models import Settlement, Region, Municipality


class DataFetcher:
    def fetch_all_settlements_with_relations(self):
        """Получить все поселения со связанными регионами и муниципалитетами"""
        return Settlement.objects.select_related(
            'municipality__region'
        ).values_list('municipality__region__name', 'municipality__name', 'population')

    def fetch_settlements_by_region(self, region_name):
        """Получить все поселения конкретного региона"""
        return Settlement.objects.filter(
            municipality__region__name=region_name
        ).select_related('municipality__region').values_list(
            'municipality__name', 'population'
        )

    def fetch_settlements_by_municipality(self, region_name, municipality_name):
        """Получить все поселения конкретного муниципалитета"""
        return list(Settlement.objects.filter(
            municipality__name=municipality_name,
            municipality__region__name=region_name
        ).values_list('population'))

    def fetch_settlement_details(self, region_name, municipality_name, search_query=None, settlement_type=None):
        """Получить подробные сведения о поселениях с фильтрацией"""
        settlements = Settlement.objects.filter(
            municipality__name=municipality_name,
            municipality__region__name=region_name
        ).select_related('municipality')

        if settlement_type:
            settlements = settlements.filter(type=settlement_type)

        if search_query:
            settlements = settlements.filter(name__icontains=search_query)

        return settlements.order_by('-population')

    def fetch_settlement_types(self, region_name, municipality_name):
        """Получить все типы поселений в муниципалитете"""
        return Settlement.objects.filter(
            municipality__name=municipality_name,
            municipality__region__name=region_name
        ).values_list('type', flat=True).distinct().order_by('type')

    def fetch_settlement_statistics(self, region_name=None, municipality_name=None):
        """Получить статистику по поселениям"""
        settlements = Settlement.objects.all()

        if region_name:
            settlements = settlements.filter(municipality__region__name=region_name)

        if municipality_name:
            settlements = settlements.filter(municipality__name=municipality_name)

        total = settlements.count()
        populated = settlements.filter(population__gt=0).count()

        return {
            'total': total,
            'populated': populated,
            'empty': total - populated
        }