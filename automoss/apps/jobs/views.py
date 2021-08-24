from django.shortcuts import render
from .models import Job

# Jobs Index View
def index(request):
    context = {"jobs" : Job.objects.all()}
    return render(request, "jobs/index.html", context)