from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    # Report Index - View Report
    path('', views.index, name='index')
]