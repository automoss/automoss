from django.urls import path, include

from . import views

app_name = 'api'

urlpatterns = [
    # Jobs
    path('jobs/', include('automoss.apps.jobs.urls')),
]