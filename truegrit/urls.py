from django.urls import re_path, path

from truegrit.views import (
    FrontPage,
    BusinessUnitListView,
)

urlpatterns = [
    re_path(
        r'^$',
        FrontPage.as_view(),
        name='frontpage'),
    path(
        'business-units/', 
        BusinessUnitListView.as_view(), 
        name='business_units'),
]    