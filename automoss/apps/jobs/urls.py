from django.urls import path, include

from . import views

app_name = 'jobs'

urlpatterns = [
    # Jobs Index - View Jobs
    path('', views.index, name='index'),
    # Reports
    path('<int:id>/report', include('automoss.apps.reports.urls'))
]