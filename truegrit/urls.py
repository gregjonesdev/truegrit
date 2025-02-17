from django.urls import re_path, path

from truegrit.views import (
    complete_time_entry,
    create_time_entry,
    Daily,
    Weekly,
    save_task,
    edit_time_entry,
    FrontPage,
    Timekeeper,
    project_detail,
    BusinessUnitListView,
    CameraManufacturerListView,
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
        'camera-manufacturers/', 
        CameraManufacturerListView.as_view(), 
        name='camera_manufacturers'),    
    path(
        'business-unit/<uuid:uuid>/', 
        BusinessUnitDetailView.as_view(), 
        name='business_unit_detail'),
    path('project/<uuid:uuid>/', project_detail, name='project_detail'),  
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
    re_path(
        r'^edit-time-entry/(?P<id>[0-9a-f-]+)/$', 
        edit_time_entry,
        name='edit_time_entry'),
    path(
        'weekly/', 
         Weekly.as_view(), 
         name='weekly'),                      
    path(
        'timekeeper/', 
        Timekeeper.as_view(), 
        name='timekeeper'),
]