from django.urls import path

from . import views

app_name = "results"

urlpatterns = [
    # View match of a result
    path('match/<uuid:match_id>/', views.ResultMatch.as_view(), name='match'),

    # Result Index - View MOSS Result
    path('', views.Index.as_view(), name="index")
]
