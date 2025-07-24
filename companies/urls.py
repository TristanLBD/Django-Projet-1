from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    # Vues pour les candidats
    path('<int:pk>/', views.company_detail, name='company_detail'),

    # Vues pour les employeurs (super_users)
    path('manage/', views.company_manage, name='company_manage'),
    path('create/', views.company_create, name='company_create'),
    path('<int:pk>/edit/', views.company_edit, name='company_edit'),
    path('<int:pk>/delete/', views.company_delete, name='company_delete'),
]
