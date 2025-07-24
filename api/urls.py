from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Export CSV des candidatures du jour
    path('export/applications/today/', views.export_applications_csv, name='export_applications_today'),

    # Import CSV des candidatures
    path('import/applications/', views.import_applications_csv, name='import_applications'),
]
