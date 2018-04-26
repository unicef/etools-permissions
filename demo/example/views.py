from django.views.generic import ListView

from demo.example.models import Organization


class OrganizationListView(ListView):
    model = Organization
