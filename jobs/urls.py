from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Vues pour les candidats
    path('', views.job_list, name='job_list'),
    path('<int:pk>/', views.job_detail, name='job_detail'),
    path('<int:pk>/apply/', views.job_apply, name='job_apply'),
    path('my-applications/', views.my_applications, name='my_applications'),

    # Vues pour les employeurs (super_users)
    path('manage/', views.job_manage, name='job_manage'),
    path('create/', views.job_create, name='job_create'),
    path('<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('<int:pk>/delete/', views.job_delete, name='job_delete'),
    path('applications/', views.application_list, name='application_list'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('applications/<int:pk>/review/', views.application_review, name='application_review'),
]
