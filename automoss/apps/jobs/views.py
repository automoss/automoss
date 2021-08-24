from ..utils.encoding import base64_decode
from .tasks import upload_to_moss
from django.shortcuts import render
from django.http.response import JsonResponse

# Jobs Index View
from .models import Job

# Jobs Index View
def index(request):
    context = {"jobs" : Job.objects.all()}
    return render(request, "jobs/index.html", context)


def new(request):
    if request.method == 'POST':

        # TODO get from database
        moss_user_id = 1

        # TODO get from request
        language = 'python'

        file_info = {
            'files': [],
            'base_files': []
        }

        for file_type in file_info:
            for f in request.FILES.getlist(file_type):
                # TODO add validation (extensions, size, etc.)

                # JSON serialise file information
                file_info[file_type].append({
                    'name': base64_decode(f.name),
                    'file': f.read()
                })

        upload_to_moss.delay(moss_user_id, language=language, **file_info)

        data = {}  # Return useful information
        return JsonResponse(data, status=200)

    else:

        context = {}
        return render(request, "jobs/new.html", context)
