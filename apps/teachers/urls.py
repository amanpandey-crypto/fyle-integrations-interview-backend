from django.urls import path
from .views import ListAssignments

urlpatterns = [
    path('assignments/',ListAssignments.as_view(),name='teachers-assignments')
]