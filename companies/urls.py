from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    # Vues pour les candidats
    path('<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),

    # Vues pour les employeurs (super_users)
    path('manage/', views.CompanyManageView.as_view(), name='company_manage'),
    path('create/', views.CompanyCreateView.as_view(), name='company_create'),
    path('<int:pk>/edit/', views.CompanyEditView.as_view(), name='company_edit'),
    path('<int:pk>/delete/', views.CompanyDeleteView.as_view(), name='company_delete'),
]
