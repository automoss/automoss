from django.urls import path, include

from . import views

app_name = "reports"

urlpatterns = [
    # TODO Generated Report - View Report
    path('match/<uuid:match_id>/', include('automoss.apps.matches.urls')),

    # Report Index - View MOSS Report
    path('', views.index, name="index")
]