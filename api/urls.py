from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('export/applications/today/', views.ExportApplicationsTodayCSVView.as_view(), name='export_applications_today'),
    path('export/applications/all/', views.ExportAllApplicationsCSVView.as_view(), name='export_applications_all'),
    path('import/applications/', views.ImportApplicationsCSVView.as_view(), name='import_applications'),
]
