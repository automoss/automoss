from django.urls import path, include

from . import views

app_name = 'jobs'

urlpatterns = [
    # Submit new job
    path('new/', views.new, name='new'),

    # Reports
    path('<uuid:job_id>/report/', include('automoss.apps.reports.urls')),
    
    # Jobs Index - View Jobs
    path('', views.index, name='index'),
]