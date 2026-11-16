from django.urls import path

from ..views import allocations

urlpatterns = [
    path("allocations/summary/", allocations.allocation_summary, name="allocation-summary"),
    path("allocations/delete/", allocations.delete_allocation, name="allocation-delete"),
]
