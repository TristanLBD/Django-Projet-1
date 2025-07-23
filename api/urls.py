from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Export CSV des candidatures du jour
    path('export/applications/today/', views.export_applications_csv, name='export_applications_today'),

    # Export CSV des candidatures avec filtres personnalisés
    path('export/applications/custom/', views.export_applications_csv_custom, name='export_applications_custom'),
]
