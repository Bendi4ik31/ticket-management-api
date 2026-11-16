from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Ticket


class TicketAPITestCase(APITestCase):

    def setUp(self):
        """Підготовка тестових даних перед кожним тестом"""
        self.user = User.objects.create_user(username='john', password='password123')
        self.staff_user = User.objects.create_superuser(username='admin', password='password123')

        self.ticket = Ticket.objects.create(
            title='Тестова проблема',
            description='Базовий опис для перевірки екшенів',
            author=self.user,
            status=Ticket.Status.OPEN
        )

    def test_create_ticket_auto_author(self):
        """1. Автоматичне підставляння автора при створенні тикета"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Новий тикет',
            'description': 'Опис звичайного тикета з низьким пріоритетом',
            'priority': 'LOW'
        }
        response = self.client.post('/api/tickets/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author'], self.user.id)

    def test_critical_ticket_validation_fails(self):
        """2. Валідація: CRITICAL тикет з описом менше 30 символів повертає 400"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Критичний панічний баг',
            'description': 'Короткий опис',  # менше 30 символів
            'priority': 'CRITICAL'
        }
        response = self.client.post('/api/tickets/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', response.data)

    def test_action_take(self):
        """3. Екшн take: змінює статус на IN_PROGRESS та призначає assigned_to"""
        self.client.force_authenticate(user=self.staff_user)
        url = f'/api/tickets/{self.ticket.id}/take/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.IN_PROGRESS)
        self.assertEqual(self.ticket.assigned_to, self.staff_user)

    def test_action_resolve_workflow(self):
        """4. Екшн resolve: забороняє закривати OPEN тикет, але закриває IN_PROGRESS"""
        self.client.force_authenticate(user=self.staff_user)
        url = f'/api/tickets/{self.ticket.id}/resolve/'

        # Спроба закрити OPEN тикет -> 400 Bad Request
        response_fail = self.client.post(url)
        self.assertEqual(response_fail.status_code, status.HTTP_400_BAD_REQUEST)

        # Переводимо в IN_PROGRESS і закриваємо -> 200 OK
        self.ticket.status = Ticket.Status.IN_PROGRESS
        self.ticket.save()

        response_success = self.client.post(url)
        self.assertEqual(response_success.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.RESOLVED)

    def test_queryset_visibility_permissions(self):
        """5. Фільтрація: звичайний юзер бачить тільки свої тикети, адмін — усі"""
        other_user = User.objects.create_user(username='other', password='password123')
        Ticket.objects.create(title='Чужий тикет', description='Опис', author=other_user)

        # Звичайний юзер бачить 1 свій тикет
        self.client.force_authenticate(user=self.user)
        res_user = self.client.get('/api/tickets/')
        self.assertEqual(len(res_user.data['results']), 1)

        # Адмін бачить 2 тикети
        self.client.force_authenticate(user=self.staff_user)
        res_admin = self.client.get('/api/tickets/')
        self.assertEqual(len(res_admin.data['results']), 2)


    def test_regular_user_cannot_take_ticket(self):
        # Arrange: логінимося звичайним юзером (не адміном)
        self.client.force_authenticate(user=self.user)
        url = f'/api/tickets/{self.ticket.id}/take/'
        
        # Act: намагаємося викликати закритий адмінський екшн
        response = self.client.post(url)
        
        # Assert: чекаємо відмову 403 Forbidden і перевіряємо, що база не чіпана
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.OPEN)
        self.assertIsNone(self.ticket.assigned_to)
