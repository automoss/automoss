from django.urls import path, include

from . import views

app_name = "results"

urlpatterns = [
    # TODO Generated Report - View Report
    path('match/<uuid:match_id>/', views.match, name='match'),

    # Report Index - View MOSS Report
    path('', views.index, name="index")
]