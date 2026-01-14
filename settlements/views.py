from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from .models import Municipality
from .facades import StatisticsFacade
from settlements.state.breadcrumb import BreadcrumbState

class StatsView(TemplateView):
    template_name = 'settlements/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        facade = StatisticsFacade()

        context['top_regions'] = facade.get_top_regions()
        context['population_stats'] = facade.get_population_stats()
        context['settlement_types'] = facade.get_settlement_types_distribution()
        context['general_stats'] = facade.get_general_stats()
        context['population_distribution'] = facade.get_population_distribution()

        breadcrumb = BreadcrumbState()
        breadcrumb.clear()
        context['breadcrumb'] = breadcrumb.get_breadcrumb()

        return context


class RegionDetailView(TemplateView):
    template_name = 'settlements/region.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        region_name = self.kwargs['region_name']

        facade = StatisticsFacade()

        context['region_stats'] = facade.get_general_stats(region_name)
        context['population_stats'] = facade.get_population_stats_by_region(region_name)
        context['municipalities'] = facade.get_municipalities_by_region(region_name)
        context['region_name'] = region_name
        context['settlement_types_chart'] = facade.get_settlement_types_distribution(
            Q(municipality__region__name=region_name)
        )
        context['population_distribution'] = facade.get_population_distribution(
            Q(municipality__region__name=region_name)
        )

        breadcrumb = BreadcrumbState()
        breadcrumb.set_region(region_name)
        context['breadcrumb'] = breadcrumb.get_breadcrumb()

        return context


class MunicipalityDetailView(TemplateView):
    template_name = 'settlements/municipality.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        region_name = self.kwargs['region_name']
        municipality_name = self.kwargs['municipality_name']

        municipality = get_object_or_404(
            Municipality,
            name=municipality_name,
            region__name=region_name
        )

        search_query = self.request.GET.get('search', '')
        settlement_type = self.request.GET.get('type', '')
        page_number = self.request.GET.get('page', 1)

        context['municipality'] = municipality
        context['region_name'] = region_name

        facade = StatisticsFacade()

        context['population_stats'] = facade.get_municipality_population_stats(
            region_name, municipality_name
        )
        context['general_stats'] = facade.get_municipality_general_stats(
            region_name, municipality_name
        )

        settlements = facade.get_municipality_settlements(
            region_name, municipality_name, search_query, settlement_type
        )

        paginator = Paginator(settlements, self.paginate_by)
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['search_query'] = search_query
        context['selected_type'] = settlement_type
        context['settlement_types'] = facade.get_settlement_types(
            region_name, municipality_name
        )
        context['total_results'] = paginator.count
        context['settlement_types_chart'] = facade.get_settlement_types_distribution(
            Q(municipality__name=municipality_name, municipality__region__name=region_name)
        )
        context['population_distribution'] = facade.get_population_distribution(
            Q(municipality__name=municipality.name, municipality__region__name=region_name)
        )

        breadcrumb = BreadcrumbState()
        breadcrumb.set_region(region_name)
        breadcrumb.set_municipality(municipality_name)
        context['breadcrumb'] = breadcrumb.get_breadcrumb()

        return context