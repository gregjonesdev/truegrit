from django.urls import re_path, path

from truegrit.views import (
    FrontPage,
    Timekeeper,
    BusinessUnitListView,
    BusinessUnitDetailView,
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
    path(
        'business-unit/<uuid:uuid>/', 
        BusinessUnitDetailView.as_view(), 
        name='business_unit_detail'),
    path(
        'timekeeper/', 
        Timekeeper.as_view(), 
        name='timekeeper'),
]