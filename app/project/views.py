"""
Views for Project APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Project
from project import serializers


class ProjectViewSet(viewsets.ModelViewSet):
    """VIew for managing Project API's"""
    serializer_class = serializers.ProjectDetailSerializer
    queryset = Project.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Modifying the queryset to filter by User"""
        return self.queryset.filter(
            createdBy=self.request.user
        ).order_by('-id')

    def get_serializer_class(self):
        """Modify the serializer class for different serializers"""
        if self.action == 'list':
            return serializers.ProjectSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Project"""
        serializer.save(createdBy=self.request.user)
