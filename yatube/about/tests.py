from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class StaticAboutUrlTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_use_right_reverse(self):
        """ проверит соответствие /about/author/ и reverse('about:author') """
        address_and_reverse = [
            ('/about/author/', reverse('about:author')),
            ('/about/tech/', reverse('about:tech'))
        ]
        for address, reversed_page in address_and_reverse:
            with self.subTest():
                self.assertEqual(address, reversed_page)

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов /about/."""
        address_and_status = [
            (reverse('about:author'), HTTPStatus.OK),
            (reverse('about:tech'), HTTPStatus.OK)
        ]
        for address, status in address_and_status:
            with self.subTest(status=status):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для адресов /about/."""
        templates = [
            ('about/author.html', reverse('about:author')),
            ('about/tech.html', reverse('about:tech'))
        ]
        for template, address in templates:
            with self.subTest(addres=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_about_uses_correct_template(self):
        """URL-адрес /about/ использует соответствующий шаблон.
        и проверка соответсвия /адреса/ и имя:приложение"""
        templates_pages_names = [
            ('about/author.html', reverse('about:author')),
            ('about/tech.html', reverse('about:tech')),
        ]

        for template, reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
