from django.shortcuts import redirect

def root(request):
    """ Redirect requests from root to login """
    return redirect("users:login")
