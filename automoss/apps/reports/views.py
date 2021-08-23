from django.shortcuts import render

# Create your views here.
def index(request, id=-1):
    context = {"id": id}
    return render(request, 'reports/index.html', context)