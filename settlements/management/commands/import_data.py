import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from settlements.models import Region, Municipality, Settlement

SETTLEMENT_CATEGORIES = {
    'Город': ['г', 'город', 'городок', 'гп'],
    'Поселок городского типа': ['пгт', 'городское поселение', 'жилрайон'],
    'Село': ['с', 'с/п', 'село', 'сл', 'слобода'],
    'Деревня': ['д', 'д.', 'деревня', 'высел', 'высельки', 'починок'],
    'Хутор': ['х', 'хутор', 'заимка'],
    'Станица': ['ст', 'ст-ца', 'станица'],
    'Поселение коренных народов': ['аал', 'аул', 'арбан', 'улус', 'у'],
    'Станция': ['ж/д_ст', 'ж/д_платф', 'ж/д_пост', 'ж/д_рзд', 'рзд', 'рзд. п.'],
    'Коттеджный поселок': ['кп', 'дп', 'массив', 'мкр'],
    'Садоводство': ['снт', 'с/о'],
    'Рабочий поселок': ['рп', 'п/о', 'п/ст', 'казарма'],
    'Поселок': ['п', 'автодорога', 'кордон', 'остров'],
    'Прочее': ['c', 'x', 'нп', 'тер', 'л/п', 'оп', 'м', 'мп', 'с/с'],
}


def get_category(settlement_type):
    """Определяет категорию по типу НП"""
    for category, types in SETTLEMENT_CATEGORIES.items():
        if settlement_type in types:
            return category
    return 'Прочее'


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV файлу')

    def handle(self, *args, **options):
        filepath = options['csv_file']
        df = pd.read_csv(filepath, sep=',', encoding='utf-8')
        df['category'] = df['type'].apply(get_category)

        with transaction.atomic():
            region_cache = {}
            for region_name in df['region'].unique():
                region, _ = Region.objects.get_or_create(name=region_name)
                region_cache[region_name] = region

            municipality_cache = {}
            for _, row in df.iterrows():
                key = f"{row['municipality']}|{row['region']}"
                if key not in municipality_cache:
                    region = region_cache[row['region']]
                    mun, _ = Municipality.objects.get_or_create(
                        name=row['municipality'],
                        region=region
                    )
                    municipality_cache[key] = mun

            batch_size = 5000
            for start in range(0, len(df), batch_size):
                batch = df.iloc[start:start + batch_size]
                settlements_batch = []

                for _, row in batch.iterrows():
                    key = f"{row['municipality']}|{row['region']}"
                    municipality = municipality_cache[key]

                    settlements_batch.append(Settlement(
                        name=row['settlement'],
                        type=row['category'],
                        population=int(row.get('population', 0)),
                        children_population=int(row.get('children', 0)),
                        municipality=municipality
                    ))

                Settlement.objects.bulk_create(
                    settlements_batch,
                    ignore_conflicts=True,
                    batch_size=1000
                )

                self.stdout.write(f"⏳ {start + len(batch):,} / {len(df):,}")

            self.stdout.write(self.style.SUCCESS('Импорт завершен!'))
