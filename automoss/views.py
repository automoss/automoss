from django.shortcuts import redirect
from django.views import View

class Index(View):
    
    def get(self, request):
        """ Redirect requests from root to login """
        return redirect("users:login")
    
