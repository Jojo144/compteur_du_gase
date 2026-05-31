import datetime

from django.core.cache import cache
from django.db.models.functions import ExtractYear
from django.http import HttpRequest
from django.urls import reverse

from base.models import Operation, Household, Product


def cached_activity_years():
    return cache.get_or_set(
        'activity_years',
        activity_years,
        timeout=3600*24,
        version=1,
    )


def activity_years() -> list[int]:
    """ Years of activity for the GASE

    Collect the union of
    - operations dates
    - household subscriptions dates
    - current year
    """
    years = []
    for Model in [Household] + Operation.__subclasses__():
        years += list(
            Model.objects.annotate(year=ExtractYear('date'))
            .values_list('year', flat=True)
            .order_by('year')
            .distinct()
        )
    current_year = datetime.date.today().year
    years.append(current_year)
    unique_years = list(set(years))
    unique_years.sort(reverse=True)

    return unique_years


def get_referent_produit_deprecation_msg(product: Product, request: HttpRequest) -> str:
    url = request.build_absolute_uri(reverse("base:detail_product", args=(product.id,)))
    return f"""Attention ⚠️ ce produit a un référent produit paramétré. Les référent·es produit sont amenés à disparaître. Voir détails et conseils ici : <{url}>
    """
