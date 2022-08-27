import datetime

from django import forms
from django.conf import settings

from .models import Transaction, OTP
from accounts.models import UserBankAccount


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'account2',
            'transaction_type'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)

        self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):

    def clean_amount(self):
        min_deposit_amount = settings.MINIMUM_DEPOSIT_AMOUNT
        amount = self.cleaned_data.get('amount')
        account2 = None

        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )

        return amount


class WithdrawForm(TransactionForm):

    def clean_amount(self):
        account = self.account
        account2 = None
        min_withdraw_amount = settings.MINIMUM_WITHDRAWAL_AMOUNT
        balance = account.balance

        amount = self.cleaned_data.get('amount')

        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You can not withdraw more than your account balance'
            )

        return amount



"""class TransferMoneyForm(forms.Form):
    user_account = forms.CharField(max_length=200)
    beneficiary_account = forms.CharField(max_length=200)
    amount = forms.CharField(max_length=20)"""

class TransferMoneyForm(TransactionForm):

    def clean_amount(self):
        account = self.account
        account2 = self.cleaned_data.get('account2')


        min_withdraw_amount = settings.MINIMUM_WITHDRAWAL_AMOUNT

        balance = account.balance

        amount = self.cleaned_data.get('amount')

        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )

        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You can not withdraw more than your account balance'
            )

        return amount


class OTP_Form(forms.ModelForm):
    class Meta:
        model = OTP
        fields = [
            'otp',
        ]