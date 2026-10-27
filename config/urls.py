from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from portal import views, students, banks
urlpatterns = [
    path('admin/', admin.site.urls), path('',views.home,name='home'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('students/',students.student_list,name='student_list'),
    path('banks/',banks.bank_list,name='bank_list'),
    path('banks/new/',banks.bank_edit,name='bank_create'),
    path('banks/export.xlsx',banks.bank_export,name='bank_export'),
    path('banks/<int:bank_id>/edit/',banks.bank_edit,name='bank_edit'),
    path('banks/<int:bank_id>/deactivate/',banks.bank_deactivate,name='bank_deactivate'),
    path('students/new/',students.student_edit,name='student_create'),
    path('students/export.xlsx',students.student_export,name='student_export'),
    path('students/<int:student_id>/edit/',students.student_edit,name='student_edit'),
    path('students/<int:student_id>/deactivate/',students.student_deactivate,name='student_deactivate'),
    path('imports/', views.import_preview, name='import_preview'),
    path('proofs/', views.proofs_list, name='proofs_list'),
    path('superadmin/integrations/', views.integration_settings, name='integration_settings'),
    path('invoices/<int:invoice_id>/proof/', views.proof_upload, name='proof_upload'),
    path('proofs/<int:proof_id>/image/', views.proof_image, name='proof_image'),
    path('proofs/<int:proof_id>/verify/', views.proof_verify, name='proof_verify'),
    path('imports/template.xlsx', views.xlsx_template, name='xlsx_template'),
    path('accounts/login/',auth_views.LoginView.as_view(),name='login'),
    path('accounts/logout/',auth_views.LogoutView.as_view(),name='logout'),
]
