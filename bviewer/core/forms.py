# -*- coding: utf-8 -*-
import string

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import Form, RegexField, EmailField, CharField, PasswordInput


MESSAGE_USERNAME = 'This value may contain only letters, numbers and @/./+/-/_ characters.'
MESSAGE_PASS = 'Should be minimum 2 letters, 2 numbers, 2 special symbol, all unique.'
SPECIAL_SYMBOLS = '!@#$%^&*()-+='


class RegistrationForm(Form):
    username = RegexField(label='Username', regex=r'^[\w.@+-]+$', max_length=30,
                          error_messages=dict(invalid=MESSAGE_USERNAME))
    email = EmailField(label='E-mail')
    password1 = CharField(widget=PasswordInput, label='Password')
    password2 = CharField(widget=PasswordInput, label='Password (again)')

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 3:
            raise ValidationError('Should be at least 3 letters')
        return username

    def clean_password1(self):
        password = self.cleaned_data['password1']
        if len(set(password)) < 6:
            raise ValidationError(MESSAGE_PASS)
        for check in (string.digits, string.ascii_letters, SPECIAL_SYMBOLS):
            if len([i for i in password if i in check]) < 2:
                raise ValidationError(MESSAGE_PASS)
        return password

    def clean(self):
        if 'username' in self.cleaned_data and 'username' in self.cleaned_data:
            username = self.cleaned_data['username']
            email = self.cleaned_data['email']
            user = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=email))
            if user.exists():
                raise ValidationError('Such username or email already exists.')
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise ValidationError('The two password fields didn\'t match.')
        return self.cleaned_data