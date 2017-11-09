from django.test import TestCase

from .. import forms


class SignUpFormTest(TestCase):
    def test_form_has_fields(self):
        form = forms.SignUpForm()
        expected = ['username', 'email', 'password1', 'password2',]
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)
