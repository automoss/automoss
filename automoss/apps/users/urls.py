"""automoss URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('login/', views.Login.as_view(), name="login"),
    path('logout/', views.Logout.as_view(), name="logout"),
    path('register/', views.Register.as_view(), name="register"),
    path('profile/', views.Profile.as_view(), name="profile"),
    path('forgot-password/', views.ForgotPassword.as_view(), name="forgot-password"),
    path('reset-password/<uuid:uid>/<str:token>/',
         views.ResetPassword.as_view(), name="reset-password"),
    path('confirm/<uuid:uid>/<str:token>/',
         views.Confirm.as_view(), name="confirm"),
    path('confirm-email/<uuid:eid>/<str:token>/',
         views.ConfirmEmail.as_view(), name="confirm-email"),
]
