from django.urls import path, include

app_name = 'api'

# Reroute api paths to their respective handlers
urlpatterns = [
    path('jobs/', include('automoss.apps.jobs.urls')),
    path('moss/', include('automoss.apps.moss.urls')),
]
