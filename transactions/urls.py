from django.urls import path

from .views import DepositMoneyView, WithdrawMoneyView, TransactionRepostView, TransferMoneyView, transaction_graph


app_name = 'transactions'


urlpatterns = [
    path("deposit/", DepositMoneyView.as_view(), name="deposit_money"),
    path("report/", TransactionRepostView.as_view(), name="transaction_report"),
    path("withdraw/", WithdrawMoneyView.as_view(), name="withdraw_money"),
    path("transfer/", TransferMoneyView.as_view(), name="transfer_money"),
    path("transfer_history/", TransferMoneyView, name="transfer_history"),
    path("graph/", transaction_graph, name="transaction_graph"),
]
