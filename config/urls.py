from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from portal import views
urlpatterns = [
    path('admin/', admin.site.urls), path('',views.home,name='home'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('imports/', views.import_preview, name='import_preview'),
    path('proofs/', views.proofs_list, name='proofs_list'),
    path('invoices/<int:invoice_id>/proof/', views.proof_upload, name='proof_upload'),
    path('proofs/<int:proof_id>/image/', views.proof_image, name='proof_image'),
    path('proofs/<int:proof_id>/verify/', views.proof_verify, name='proof_verify'),
    path('imports/template.xlsx', views.xlsx_template, name='xlsx_template'),
    path('accounts/login/',auth_views.LoginView.as_view(),name='login'),
    path('accounts/logout/',auth_views.LogoutView.as_view(),name='logout'),
]
