from django.urls import path, include

from . import views

app_name = "reports"

urlpatterns = [
    # TODO Generated Report - View Report

    # Report Index - View MOSS Report
    path('', views.Index.as_view(), name="index")
]