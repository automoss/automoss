from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from django.views import View
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.http import Http404
from django.conf import settings

# TODO Implement handling of '?next=/url/' for redirects due to @login_required
# def login(request):
#     """ Login View : Logs user in if valid credentials supplied """
#     if request.method == "GET":
#         if request.user.is_authenticated:
#             return redirect(settings.LOGIN_REDIRECT_URL)
#         return render(request, "users/login.html")
#     elif request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             if user.is_active:
#                 django_login(request, user)
#                 #redirect_url = request.POST.get('next') or settings.LOGIN_REDIRECT_URL
#                 #if is_safe_url(redirect_url, settings.ALLOWED_HOSTS): #require_https=request.is_secure()
#                 #    return redirect(redirect_url)
#                 return redirect(settings.LOGIN_REDIRECT_URL)
#             else:
#                 return render(request, "users/login.html", {"errors": "Account diabled!"})
#         else:
#             return render(request, "users/login.html", {"errors": "The username and password entered were incorrect!"})
#     raise Http404(f"Login route with method {request.METHOD}, not found!")

class Login(View):
    """ Login view """
    template = "users/auth/login.html"

    def get(self, request):
        """ Get login view """
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return render(request, self.template)

    def post(self, request):
        """ Post login """
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                django_login(request, user)
                #redirect_url = request.POST.get('next') or settings.LOGIN_REDIRECT_URL
                #if is_safe_url(redirect_url, settings.ALLOWED_HOSTS): #require_https=request.is_secure()
                #    return redirect(redirect_url)
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                return render(request, self.template, {"errors": "Account diabled!"})
        else:
            return render(request, self.template, {"errors": "The username and password entered were incorrect!"})

@method_decorator(login_required, name='dispatch')
class Logout(View):
    """ Logout View """
    template = "users/auth/logged_out.html"

    def get(self, request):
        """ Get logout view """
        django_logout(request)
        return render(request, self.template)
    
# @login_required
# def logout(request):
#     """ Logout View : Log user out """
#     if request.method == "GET":
#         django_logout(request)
#         return render(request, "users/logged_out.html")
#     return Http404(f"Logout route with method {request.METHOD}, not found!")
    
    