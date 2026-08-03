from http import HTTPStatus

from pytils.translit import slugify

from .base import BaseNotesTestCase
from notes.models import Note


class LogicTests(BaseNotesTestCase):
    def test_authenticated_can_create_note(self):
        data = {
            'title': 'Новая заметка',
            'text': 'Текст заметки',
        }

        count_before = Note.objects.count()

        response = self.client_auth_1.post(self.add_url, data)

        self.assertRedirects(
            response,
            self.success_url,
            status_code=HTTPStatus.FOUND,
        )

        count_after = Note.objects.count()
        self.assertEqual(count_after, count_before + 1)

        note = Note.objects.get(slug=slugify(data['title']))
        self.assertEqual(note.author, self.user1)
        self.assertEqual(note.text, data['text'])
        self.assertEqual(note.title, data['title'])

    def test_anonymous_cannot_create_note(self):
        initial_count = Note.objects.filter(author=self.user1).count()
        data = {
            'title': 'Анонимная заметка',
            'text': 'Текст',
        }

        response = self.client.post(self.add_url, data, follow=False)

        final_count = Note.objects.filter(author=self.user1).count()
        self.assertEqual(final_count, initial_count)

        expected_url = f"{self.login_url}?next={self.add_url}"
        self.assertRedirects(response, expected_url)

    def test_cannot_create_two_notes_with_same_slug(self):
        initial_count = Note.objects.filter(slug=self.note.slug).count()

        data = {
            'title': 'Первая заметка',
            'text': 'Текст',
            'slug': self.note.slug,
        }

        response = self.client_auth_1.post(self.add_url, data)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        form = response.context['form']
        self.assertIn('slug', form.errors)

        current_count = Note.objects.filter(slug=self.note.slug).count()
        self.assertEqual(
            current_count,
            initial_count,
            "При попытке создания заметки с существующим slug "
            "количество записей в БД изменилось"
        )

    def test_slug_generated_automatically_if_not_provided(self):
        Note.objects.all().delete()

        title = 'Заметка без slug'
        data = {'title': title, 'text': 'Текст'}

        response = self.client_auth_1.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        note = Note.objects.filter(title=title, author=self.user1)
        self.assertEqual(
            note.count(),
            1,
            "Должно быть создано ровно 1 заметка с таким заголовком и автором")
        note = note.first()
        expected_slug = slugify(title)
        self.assertEqual(note.slug, expected_slug)

    def test_user_can_edit_own_note(self):
        note = self.edit_note
        edit_url = self.get_edit_url(note.slug)

        new_title = 'Отредактированная заметка'
        data = {
            'title': new_title,
            'text': 'Новый текст'
        }
        response = self.client_auth_1.post(edit_url, data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        if 'form' in response.context:
            form = response.context['form']
            self.assertFalse(form.errors, f"Форма невалидна: {form.errors}")

        note_updated = Note.objects.get(pk=note.pk)
        self.assertEqual(note_updated.title, new_title)
        self.assertEqual(note_updated.text, data['text'])
        self.assertEqual(note_updated.author, note.author)
        self.assertEqual(
            note_updated.slug,
            slugify(new_title),
            f"Slug должен совпадать с slugify('{new_title}'),"
            "но получилось '{note_updated.slug}'"
        )

    def test_user_cannot_edit_other_user_note(self):
        note = self.note2
        edit_url = self.get_edit_url(note.slug)

        data = {
            'title': 'Попытка изменить чужую заметку',
            'text': 'Совершенно новый текст, которого раньше не было'
        }

        response = self.client_auth_1.post(edit_url, data, follow=False)

        note_after = Note.objects.get(pk=note.pk)

        self.assertEqual(note_after.title, note.title)
        self.assertEqual(note_after.text, note.text)
        self.assertEqual(note_after.slug, note.slug)
        self.assertEqual(note_after.author, note.author)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_can_delete_own_note(self):
        note = self.note

        response = self.client_auth_1.post(self.delete_url, follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(Note.objects.filter(pk=note.pk).exists())

    def test_user_cannot_delete_other_user_note(self):
        note = self.note2

        response = self.client_auth_1.post(self.delete_url, follow=False)

        self.assertTrue(Note.objects.filter(pk=note.pk).exists())
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
