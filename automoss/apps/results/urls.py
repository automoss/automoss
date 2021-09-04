from django.urls import path, include

from . import views

app_name = "results"

urlpatterns = [
    # TODO Generated Report - View Report
    path('match/<uuid:match_id>/', views.ResultMatch.as_view(), name='match'),

    # Report Index - View MOSS Report
    path('', views.Index.as_view(), name="index")
]