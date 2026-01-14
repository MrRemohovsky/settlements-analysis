from typing import List, Tuple


class BreadcrumbState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._current_region = None
        self._current_municipality = None

        self._initialized = True

    def set_region(self, region_name: str) -> None:
        """
        Установить текущий регион.
        Автоматически очищает муниципалитет.

        Args:
            region_name: Название региона
        """
        self._current_region = region_name
        self._current_municipality = None

    def set_municipality(self, municipality_name: str) -> None:
        """
        Установить текущий муниципалитет.
        Требует, чтобы регион уже был установлен.
        """
        if not self._current_region:
            raise ValueError("Сначала установите регион через set_region()")

        self._current_municipality = municipality_name

    def get_breadcrumb(self) -> List[Tuple[str, str]]:
        """
        Получить список хлебных крошек.
        """
        breadcrumb = [
            ('Главная', '/settlements/'),
        ]

        if self._current_region:
            region_url = f"/settlements/regions/{self._current_region}/"
            breadcrumb.append((self._current_region, region_url))

        if self._current_municipality and self._current_region:
            municipality_url = f"/settlements/regions/{self._current_region}/{self._current_municipality}/"
            breadcrumb.append((self._current_municipality, municipality_url))

        return breadcrumb

    def clear(self) -> None:
        """Очистить навигацию (вернуться на главную)"""
        self._current_region = None
        self._current_municipality = None
