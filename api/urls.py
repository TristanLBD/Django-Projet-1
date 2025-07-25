from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Export CSV des candidatures du jour
    path('export/applications/today/', views.ExportApplicationsCSVView.as_view(), name='export_applications_today'),

    # Import CSV des candidatures
    path('import/applications/', views.ImportApplicationsCSVView.as_view(), name='import_applications'),
]
