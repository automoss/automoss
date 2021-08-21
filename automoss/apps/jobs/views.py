from django.shortcuts import render

# Create your views here.
def index(request):
    context = {"jobs": [(1, "Job 1"), (2, "Job 2"), (3, "Job 3"), (4, "Job 4"), (5, "Job 5")]}
    return render(request, "jobs.html", context)