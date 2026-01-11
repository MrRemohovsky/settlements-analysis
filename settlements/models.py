from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Регион")

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"

    def __str__(self):
        return self.name


class Municipality(models.Model):
    name = models.CharField(max_length=200, verbose_name="Муниципалитет")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='municipalities')

    class Meta:
        verbose_name = "Муниципалитет"
        verbose_name_plural = "Муниципалитеты"
        unique_together = ['name', 'region']

    def __str__(self):
        return f"{self.name} ({self.region.name})"


class Settlement(models.Model):
    name = models.CharField(max_length=200, verbose_name="Населенный пункт")
    type = models.CharField(max_length=50, verbose_name="Тип НП")
    population = models.PositiveIntegerField(null=True, blank=True, verbose_name="Население")
    children_population = models.PositiveIntegerField(null=True, blank=True, verbose_name="Дети")

    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, related_name='settlements')

    class Meta:
        verbose_name = "Населенный пункт"
        verbose_name_plural = "Населенные пункты"

    def __str__(self):
        return f"{self.name} ({self.type})"
