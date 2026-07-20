from rest_framework import generics

from activities.models import ActivityLog
from activities.serializers import ActivitySerializer


class ActivitiesList(generics.ListAPIView):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivitySerializer
