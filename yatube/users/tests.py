from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class StaticUsersUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Testometr')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов /users/ и соответсвие users:name."""
        users_pages_list = [
            ('/auth/signup/', reverse('users:signup')),
            ('/auth/login/', reverse('users:login')),
            ('/auth/password_reset/', reverse('users:password_reset')),
            ('/auth/password_reset/done/',
             reverse('users:password_reset_done')),
            ('/auth/password_change/', reverse('users:password_change')),
            ('/auth/password_change/done/',
                reverse('users:password_change_done')),
            ('/auth/logout/', reverse('users:logout'))
        ]

        for address, reversed_page in users_pages_list:
            with self.subTest():
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertEqual(address, reversed_page)

    def test_users_urls_uses_correct_template(self):
        """Проверяем, что URL-адрес Users использует нужный шаблон."""
        templates_url_names = [
            (reverse('users:signup'), 'users/signup.html'),
            (reverse('users:login'), 'users/login.html'),
            (reverse('users:password_reset'),
             'users/password_reset_form.html'),
            (reverse('users:password_reset_done'),
             'users/password_reset_done.html'),
            (reverse('users:password_change'),
                'users/password_change_form.html'),
            (reverse('users:password_change_done'),
                'users/password_change_done.html'),
            (reverse('users:logout'), 'users/logged_out.html')
        ]

        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_users_signup_form(self):
        """Проверьте передаётся ли форма для создания нового пользователя"""
        response = self.guest_client.get(reverse('users:signup'))
        self.assertIn('form', response.context)

    def test_new_user_create(self):
        """создадим ли мы нового пользвателя? =)"""
        form_data = {
            'first_name': 'Yamaha',
            'last_name': 'MT-10',
            'username': 'MoToTayka',
            'email': 'otskrebay@govno.ru',
            'password1': '123E456Be',
            'password2': '123E456Be',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertTrue(User.objects.filter(username='MoToTayka').exists())
