from django.urls import re_path, path

from truegrit.views import (
    FrontPage,
)

urlpatterns = [
    re_path(
        r'^$',
        FrontPage.as_view(),
        name='frontpage'),
]