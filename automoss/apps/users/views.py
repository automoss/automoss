from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Redirect to jobs/
@login_required
def home(request):
    return redirect("jobs:index")