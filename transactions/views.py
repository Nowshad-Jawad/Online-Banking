from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect, HttpResponseRedirect

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView
from django.db import transaction
from transactions.constants import DEPOSIT, WITHDRAWAL, TRANSFER
from transactions.forms import (
    DepositForm,
    WithdrawForm,
    TransferMoneyForm,
)
from django.core.mail import send_mail
from transactions.models import Transaction
from accounts.models import UserBankAccount
from .utils import get_plot
from django.conf import settings
import random


class TransactionRepostView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    form_data = {}

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
        })

        return context


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transactions:transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })

        return context


class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit Money to Your Account'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account

        account.balance += amount
        account.save(
            update_fields=[
                'balance',
            ]
        )

        messages.success(
            self.request,
            f'{amount}$ was deposited to your account successfully'
        )

        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money from Your Account'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        self.request.user.account.balance -= form.cleaned_data.get('amount')
        self.request.user.account.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'Successfully withdrawn {amount}$ from your account'
        )

        return super().form_valid(form)


"""def TransferMoneyView(request):

    if request.method == 'POST':
        form = TransferMoneyForm(request.POST)
        if form.is_valid():
            account1 = form.cleaned_data.get('user_account')
            account2 = form.cleaned_data.get('beneficiary_account')
            amount = form.cleaned_data.get('amount')

            account1_obj = UserBankAccount.objects.get(account_no = account1)
            account1_obj.balance -= int(amount)
            account1_obj.save()

            account2_obj = UserBankAccount.objects.get(account_no=account2)
            account2_obj.balance += int(amount)
            account2_obj.save()

            messages.success(request, 'Amount Transferred')
            return render(request,'transactions/transfer_history.html', {'form':form})

    else:
        form = TransferMoneyForm()

    return render(request, 'transactions/transfer_money.html', {'form':form})"""


class TransferMoneyView(TransactionCreateMixin):
    form_class = TransferMoneyForm
    title = 'Transfer Money from Your Account'

    def get_initial(self):
        initial = {'transaction_type': TRANSFER}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        account2 = form.cleaned_data['account2']


        self.request.user.account.balance -= form.cleaned_data.get('amount')
        self.request.user.account.save(update_fields=['balance'])

        account2_obj = UserBankAccount.objects.get(account_no=int(account2))
        account2_obj.balance += int(amount)
        account2_obj.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'Successfully transferred {amount} from your account to {account2}.'
        )

        return super().form_valid(form)

        return HttpResponseRedirect(
            reverse_lazy('transactions:transaction_report')
        )













def transaction_graph(request):
    if request.user.is_authenticated:
        account = []
        account.append(Transaction.objects.all())
        x = []
        y = []

        qs = Transaction.objects.filter(account= account)
        x = [x.user.account.transaction_type for x in qs]
        y = [y.user.account.ammount for y in qs]
        chart = get_plot(x, y)
        return render(request, 'transactions/transaction_graph.html', {'chart':chart})
