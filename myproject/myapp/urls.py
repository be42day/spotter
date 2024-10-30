from django.urls import path
from . import views

urlpatterns = [
    path('process-data/', views.process_data, name='process_data'),
]