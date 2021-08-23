from django.urls import path, include

from . import views

app_name = 'jobs'

urlpatterns = [
    # Jobs Index - View Jobs
    path('', views.index, name='index'),
    # Jobs Index - New
    path('new', views.new, name='new'),
    # Reports
    path('<int:id>/report', include('automoss.apps.reports.urls'))
]