# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from app import views

urlpatterns = [
    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.
    re_path(r'^.*\.html', views.pages, name='pages'),

    # The home page
    path('', views.index, name='home'),
    path('update-profile', views.update_profile),
    path('change-password', views.change_password),
    path('manage-user', views.manage_user),
    path('remove-user', views.remove_user),
    path('enable-user', views.enable_user),
    path('disable-user', views.disable_user),
    path('add-user', views.add_user),
    path('patch', views.patch),
    path('do-upload', views.do_upload),
    re_path(r'download-patch/(?P<service>[A-Za-z0-9]+)/$', views.download_patch),
    re_path(r'upload-page/(?P<service>[A-Za-z0-9]+)/$', views.upload_page),
]
