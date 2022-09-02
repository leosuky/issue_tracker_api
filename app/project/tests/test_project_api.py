"""
Test Project APIs
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Project

from project.serializers import ProjectSerializer, ProjectDetailSerializer


PROJECT_URL = reverse('project:project-list')


def detail_url(project_id):
    """Create and return a project detail url"""
    return reverse('project:project-detail', args=[project_id])


# Helper functions to create projects for testing
def create_project(createdBy, **kwargs):
    """Create and return a new project"""
    data = {
        'title': 'Ecommerce Clothing App',
        'description': 'A clothing store web app with React and Django',
        'status': 'Design'
    }
    data.update(**kwargs)

    project = Project.objects.create(createdBy=createdBy, **data)
    return project


def create_user(**kwargs):
    """Create and Return a new User"""
    return get_user_model().objects.create_user(**kwargs)


class PublicProjectAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required to access API"""
        res = self.client.get(PROJECT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProjectAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_projects(self):
        """Test retrieving a list of projects"""
        create_project(createdBy=self.user)
        create_project(createdBy=self.user)
        create_project(createdBy=self.user)

        res = self.client.get(PROJECT_URL)

        projects = Project.objects.all().order_by('-id')
        serializer = ProjectSerializer(projects, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_project_is_limited_to_user(self):
        """Test list of project returned is only for authenticated user"""
        other_user = create_user(
            email='otherDude@example.com',
            password='Defautl$123'
        )
        create_project(createdBy=other_user)
        create_project(createdBy=self.user)

        res = self.client.get(PROJECT_URL)

        projects = Project.objects.filter(createdBy=self.user)
        serializer = ProjectSerializer(projects, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test GET project detail"""
        project = create_project(createdBy=self.user)

        url = detail_url(project.id)
        res = self.client.get(url)

        serializer = ProjectDetailSerializer(project)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a Project"""
        payload = {
            'title': 'Creating a Text Editor',
            'status': 'Design',
            'description': 'A super powerful text editor for all Mac'
        }
        res = self.client.post(PROJECT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(project, k), v)
        self.assertEqual(project.createdBy, self.user)

    def test_partial_update(self):
        """Test partial update of project"""
        init_desc = 'Operating System with Golang'
        project = create_project(
            createdBy=self.user,
            title='Brand New OS',
            status='Design',
            description=init_desc
        )

        payload = {'title': 'Same Old OS'}
        url = detail_url(project.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        self.assertEqual(project.title, payload['title'])
        self.assertEqual(project.description, init_desc)
        self.assertEqual(project.createdBy, self.user)

    def test_full_update(self):
        """Test full update of project"""
        project = create_project(
            createdBy=self.user,
            title='Brand New OS',
            status='Design',
            description='Operating System with Golang'
        )

        payload = {
            'title': 'Creating a Text Editor',
            'status': 'Design',
            'description': 'A super powerful text editor for all Mac'
        }
        url = detail_url(project.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(project, k), v)
        self.assertEqual(project.createdBy, self.user)

    def test_update_user_returns_error(self):
        """Test changing the project user results in an error"""
        new_user = create_user(
            email='newuser@example.com',
            password='Defautl$123'
        )
        project = create_project(createdBy=self.user)

        payload = {'createdBy': new_user.id}
        url = detail_url(project.id)
        self.client.patch(url, payload)

        project.refresh_from_db()
        self.assertEqual(project.createdBy, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successfully"""
        project = create_project(createdBy=self.user)

        url = detail_url(project.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=project.id).exists())

    def test_delete_other_users_project_error(self):
        """Test trying to delete another users project gives error"""
        new_user = create_user(
            email='newuser@example.com',
            password='Defautl$123'
        )
        project = create_project(createdBy=new_user)

        url = detail_url(project.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Project.objects.filter(id=project.id).exists())
