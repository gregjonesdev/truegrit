from django.urls import re_path, path

from truegrit.views import (
    complete_time_entry,
    create_time_entry,
    Daily,
    Weekly,
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
        'complete-time-entry/', 
         complete_time_entry, 
         name='complete_time_entry'),     
    path(
        'save-task/', 
         save_task, 
         name='save_task'),
    path(
        'daily/', 
         Daily.as_view(), 
         name='dailytime'),  
    path(
        'weekly/', 
         Weekly.as_view(), 
         name='weekly'),                      
    path(
        'timekeeper/', 
        Timekeeper.as_view(), 
        name='timekeeper'),
]