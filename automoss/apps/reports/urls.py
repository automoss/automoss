from django.urls import path, include

from . import views

app_name = "reports"

urlpatterns = [
    # Download
    path('download', views.Index.download_pdf, name="download")
]