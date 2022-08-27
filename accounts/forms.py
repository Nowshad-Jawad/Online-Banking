from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db import transaction

from .models import User, UserBankAccount, UserAddress, Profile
from .constants import GENDER_CHOICE


class UserAddressForm(forms.ModelForm):

    class Meta:
        model = UserAddress
        fields = [
            'street_address',
            'city',
            'postal_code',
            'country'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({})


class UserRegistrationForm(UserCreationForm):
    gender = forms.ChoiceField(choices=GENDER_CHOICE)
    birth_date = forms.DateField()

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({})

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()


            gender = self.cleaned_data.get('gender')
            birth_date = self.cleaned_data.get('birth_date')

            UserBankAccount.objects.create(
                user=user,
                gender=gender,
                birth_date=birth_date,
                account_no=(
                    user.id + settings.ACCOUNT_NUMBER_START_FROM
                )
            )
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(label=("Password"), widget=forms.PasswordInput)
    account_no = forms.IntegerField()
    pin = forms.IntegerField(label=("Account Pin"), widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        account_no = self.cleaned_data.get('account_no')
        pin = self.cleaned_data.get('pin')

        if email and password and pin:
            user = authenticate(email=email, password=password, account_no=account_no, pin=pin)

            if not user:
                raise forms.ValidationError('Email does not exist')

            if not password:
                raise forms.ValidationError('Incorrect Password')

            if not account_no:
                raise forms.ValidationError('Incorrect Account Number')

            if not pin:
                raise forms.ValidationError('Incorrect Pin')


        return super(UserLoginForm, self).clean(*args, **kwargs)






class UserProfileForm(forms.ModelForm):
    password = None
    class Meta:
        model = UserBankAccount
        fields = ['user', 'gender', 'birth_date', 'balance']
        labels = {'balance' : 'Balance'}


class EditUserProfileForm(UserChangeForm):
    password = None
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        labels = {'first_name' : 'First Name', 'last_name' : 'Last Name'}

class EditUserAddressForm(UserChangeForm):
    password = None
    class Meta:
        model = UserAddress
        fields = ['street_address', 'city', 'postal_code', 'country']
        labels = {'street_address' : 'Street Address', 'city' : 'City', 'postal_code' : 'Postal Code', 'country' : 'Country'}


class AccountPinForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'pin',
        ]
        labels = {'pin' : 'Set Account Pin'}