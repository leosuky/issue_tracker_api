"""
Serializers for Project API
"""
from rest_framework import serializers

from core.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Projects"""

    class Meta:
        model = Project
        fields = ['id', 'title', 'status']
        read_only_fields = ['id']


class ProjectDetailSerializer(ProjectSerializer):
    """Serialzer for Project detail"""

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['description', 'createdAt']
