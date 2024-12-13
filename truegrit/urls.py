from django.urls import re_path, path

from truegrit.views import (
    create_time_entry,
    save_task,
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
        'create-time-entry/', 
         create_time_entry, 
         name='create_time_entry'),
    path(
        'save-task/', 
         save_task, 
         name='save_task'),             
    path(
        'timekeeper/', 
        Timekeeper.as_view(), 
        name='timekeeper'),
]