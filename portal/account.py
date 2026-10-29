from django import forms
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from .models import UserProfile
from .proofs import validate_image

class PortalLoginView(LoginView):
    def get_success_url(self):
        # The dashboard is the landing page for all signed-in roles.
        from django.urls import reverse
        return reverse('dashboard')

    def form_valid(self,form):
        response=super().form_valid(form)
        UserProfile.objects.get_or_create(user=self.request.user)
        return response

class ProfileForm(forms.Form):
    first_name=forms.CharField(max_length=150,label='Nama depan')
    last_name=forms.CharField(max_length=150,required=False,label='Nama belakang')
    photo=forms.FileField(required=False,label='Foto profil JPG/PNG (maks. 2 MB)')

@login_required
def profile(request):
    user=request.user
    user_profile,_=UserProfile.objects.get_or_create(user=user)
    form=ProfileForm(request.POST or None,request.FILES or None,initial={'first_name':user.first_name,'last_name':user.last_name})
    if request.method=='POST' and form.is_valid():
        if form.cleaned_data['photo']:
            try:
                data,kind=validate_image(form.cleaned_data['photo'])
                user_profile.photo=data;user_profile.photo_type=kind
            except ValueError as exc:
                form.add_error('photo',str(exc))
        if not form.errors:
            user.first_name=form.cleaned_data['first_name'];user.last_name=form.cleaned_data['last_name']
            user.save(update_fields=['first_name','last_name'])
            user_profile.save(update_fields=['photo','photo_type'])
            return redirect('profile')
    return render(request,'portal/profile.html',{'form':form,'has_photo':bool(user_profile.photo)})

@login_required
def profile_photo(request):
    profile=getattr(request.user,'shb_profile',None)
    if not profile or not profile.photo: raise Http404
    response=HttpResponse(bytes(profile.photo),content_type='image/jpeg' if profile.photo_type=='jpeg' else 'image/png')
    response['Cache-Control']='private, no-store';response['X-Content-Type-Options']='nosniff'
    return response

@login_required
def change_password(request):
    form=PasswordChangeForm(request.user,request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=form.save();update_session_auth_hash(request,user)
        profile,_=UserProfile.objects.get_or_create(user=user)
        profile.must_change_password=False;profile.save(update_fields=['must_change_password'])
        return redirect('dashboard')
    return render(request,'portal/change_password.html',{'form':form})
