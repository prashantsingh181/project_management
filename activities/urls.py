from django.urls import path

from activities.views import ActivitiesList

urlpatterns = [path("", ActivitiesList.as_view())]
