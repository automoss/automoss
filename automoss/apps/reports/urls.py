from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    # TODO Generated Report - View Report
    #path('<uuid:report_id>/', views.report, name='report'),
    # Report Index - View MOSS Report
    path('', views.index, name="index")
]