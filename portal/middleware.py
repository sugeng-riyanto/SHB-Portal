from django.shortcuts import redirect
from django.urls import reverse

class RequirePasswordChangeMiddleware:
    """Enforce change for profiles provisioned when the user signs in."""
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        if request.user.is_authenticated:
            profile=getattr(request.user,'shb_profile',None)
            allowed={reverse('change_password'),reverse('logout')}
            if profile and profile.must_change_password and request.path not in allowed and not request.path.startswith('/static/'):
                return redirect('change_password')
        return self.get_response(request)
