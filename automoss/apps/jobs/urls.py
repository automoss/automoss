from django.urls import path, include

from . import views

app_name = 'jobs'

urlpatterns = [
    # Submit new job
    path('new', views.New.as_view(), name='new'),
    path('cancel', views.Cancel.as_view(), name='cancel'),
    path('remove', views.Remove.as_view(), name='remove'),
    path('retry', views.Retry.as_view(), name='retry'),

    # Results
    path('<uuid:job_id>/result/',
         include('automoss.apps.results.urls'), name='result'),

    # Jobs Index - View Jobs
    path('', views.Index.as_view(), name='index'),
]

apipatterns = [
    # Get jobs data
    path('get_jobs', views.JSONJobs.as_view(), name='get_jobs'),

    # Get statuses of jobs
    path('get_statuses', views.JSONStatuses.as_view(), name='get_statuses'),

    # Get log of jobs
    path('get_logs', views.JSONJobEvents.as_view(), name='get_logs'),
]

urlpatterns += apipatterns
