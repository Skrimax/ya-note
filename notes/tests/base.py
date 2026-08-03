from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class BaseNotesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='krosh', password='123')
        cls.user2 = User.objects.create_user(username='zadira', password='123')

        cls.note = Note.objects.create(
            author=cls.user1,
            title='Заметка пользователя 1',
            slug='note-1'
        )
        cls.note2 = Note.objects.create(
            author=cls.user2,
            title='Заметка пользователя 2',
            slug='note-2'
        )

        cls.edit_note = Note.objects.create(
            author=cls.user1,
            title='Тестовая заметка для редактирования',
            slug='test-edit-note'
        )

        cls.home_url = reverse('notes:home')
        cls.notes_list_url = reverse('notes:list')
        cls.success_url = reverse('notes:success')
        cls.add_url = reverse('notes:add')
        cls.detail_url = reverse('notes:detail', args=[cls.note.slug])
        cls.edit_url = reverse('notes:edit', args=[cls.note.slug])
        cls.delete_url = reverse('notes:delete', args=[cls.note.slug])

        cls.login_url = reverse('users:login')
        cls.signup_url = reverse('users:signup')
        cls.logout_url = reverse('users:logout')

        client_auth_1 = Client()
        client_auth_1.force_login(cls.user1)
        cls.client_auth_1 = client_auth_1

        client_auth_2 = Client()
        client_auth_2.force_login(cls.user2)
        cls.client_auth_2 = client_auth_2

    @classmethod
    def get_edit_url(cls, slug: str) -> str:
        return reverse('notes:edit', args=[slug])
