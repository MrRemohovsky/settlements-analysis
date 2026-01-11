from django.db.models import Q
from django.views.generic import TemplateView

from .services import (
    TotalStatsService,
)
from .services.municipality_service import MunicipalityStatsService


class StatsView(TemplateView):
    template_name = 'settlements/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_regions'] = TotalStatsService.get_top_regions()
        context['population_stats'] = TotalStatsService.get_population_stats()
        context['settlement_types'] = TotalStatsService.get_settlement_types_distribution()
        context['general_stats'] = TotalStatsService.get_general_stats()
        return context


class RegionDetailView(TemplateView):
    """Детали конкретного РЕГИОНА"""

    template_name = 'settlements/region.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        region_name = self.kwargs['region_name']

        context['region_stats'] = TotalStatsService.get_general_stats(region_name)
        context['population_stats'] = TotalStatsService.get_population_stats_by_region(region_name)
        context['municipalities'] = MunicipalityStatsService.get_municipalities_by_region(region_name)

        return context
