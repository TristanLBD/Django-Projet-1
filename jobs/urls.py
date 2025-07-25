from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Vues pour les candidats
    path('', views.JobListView.as_view(), name='job_list'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('<int:pk>/apply/', views.JobApplyView.as_view(), name='job_apply'),
    path('my-applications/', views.MyApplicationsView.as_view(), name='my_applications'),

    # Vues pour les employeurs (super_users)
    path('manage/', views.JobManageView.as_view(), name='job_manage'),
    path('create/', views.JobCreateView.as_view(), name='job_create'),
    path('<int:pk>/edit/', views.JobEditView.as_view(), name='job_edit'),
    path('<int:pk>/delete/', views.JobDeleteView.as_view(), name='job_delete'),
    path('applications/', views.ApplicationListView.as_view(), name='application_list'),
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('applications/<int:pk>/review/', views.ApplicationReviewView.as_view(), name='application_review'),
]
