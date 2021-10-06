from django.urls import path

from . import views

app_name = 'moss'


urlpatterns = [
    # Get moss status
    path('get_status', views.MossStatus.as_view(), name='get_status'),
]
