from django.contrib.auth.models import User
from django import forms

from account.models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Пароли не совпадают")
        return cd['password2']

    def clean_email(self):
        return self.check_unique('email')

    def clean_username(self):
        return self.check_unique('username')

    def check_unique(self, field: str):
        data = self.cleaned_data[field]
        if User.objects.filter(**{field: data}).exists():
            raise forms.ValidationError(f'{field.capitalize()} уже занят.')
        return data


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        return self.check_unique('email')

    def clean_username(self):
        return self.check_unique('username')

    def check_unique(self, field: str):
        data = self.cleaned_data[field]
        qs = User.objects.exclude(id=self.instance.id).filter(**{field: data})
        if qs.exists():
            raise forms.ValidationError(f'{field.capitalize()} already in use')
        return data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('blog_name', 'date_of_birth', 'photo')
