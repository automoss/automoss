
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http.response import JsonResponse
from django.views import View

from .pinger import Pinger


@method_decorator(login_required, name='dispatch')
class MossStatus(View):
    """ JSON view of Jobs """

    def get(self, request):
        """ Get user's jobs """
        status, current_ping, average_ping = Pinger.determine_load()
        data = {
            'status': status,
            'current_ping': current_ping,
            'average_ping': average_ping
        }
        return JsonResponse(data, status=200)
