from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import HttpResponseRedirect, render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.conf import settings
import uuid

from.models import Profile, UserBankAccount
from .forms import UserRegistrationForm, UserAddressForm, UserProfileForm, EditUserProfileForm, EditUserAddressForm, AccountPinForm, UserLoginForm


User = get_user_model()


class UserRegistrationView(TemplateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/user_registration.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse_lazy('transactions:transaction_report')
            )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        registration_form = UserRegistrationForm(self.request.POST)
        address_form = UserAddressForm(self.request.POST)

        if registration_form.is_valid() and address_form.is_valid():
            user = registration_form.save()
            address = address_form.save(commit=False)
            address.user = user
            address.save()

            uid = uuid.uuid4()
            account_no = user.id + settings.ACCOUNT_NUMBER_START_FROM
            pro_obj = Profile(user=user, token=uid, account_no=account_no)
            pro_obj.save()



            send_email_after_registration(user.email, uid, account_no)


            messages.success(request, 'Account Created Successfully,To verify your account check your email' )

            return redirect('/accounts/register/')

        return self.render_to_response(
            self.get_context_data(
                registration_form=registration_form,
                address_form=address_form
            )
        )

    def get_context_data(self, **kwargs):
        if 'registration_form' not in kwargs:
            kwargs['registration_form'] = UserRegistrationForm()
        if 'address_form' not in kwargs:
            kwargs['address_form'] = UserAddressForm()

        return super().get_context_data(**kwargs)


class UserLoginView(LoginView):
    template_name='accounts/user_login.html'
    redirect_authenticated_user = False

    def get(self, request):
        form = UserLoginForm
        return render(request, 'accounts/user_login.html', {'form':form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            password = form.cleaned_data['password']
            account_no = form.cleaned_data['account_no']
            pin = form.cleaned_data['pin']

            user = authenticate(email=email, password=password, account_no=account_no, pin=pin)
            pro = Profile.objects.get(account_no=account_no)
            if pro.verify:
                login(request, user)
                #return render(request, 'accounts/user_profile.html')
                return HttpResponseRedirect(
                    reverse_lazy('transactions:deposit_money')
                )
            else:
                messages.info(request, "Your account is not verified, please check your mail and verify your account.")
                return redirect('accounts/register/')



"""def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('passowrd')
            pin=form.cleaned_data.get('pin')

            user = User.objects.get(email=email)

            if user == None:
                raise ValueError("Email does not exist")

            if password == user.password and pin == Profile.user.pin:
                login(request, user)
            else:
                raise ValueError("Incorrect password or pin!")

    else:
        form = UserLoginForm
    return render(request, 'accounts/user_login.html', {'form':form})"""

class LogoutView(RedirectView):
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        return super().get_redirect_url(*args, **kwargs)




def profile_purpose(request):
    if request.user.is_authenticated:
        form = UserProfileForm(instance=request.user.account)
        return render(request, 'accounts/user_profile.html', {'name':request.user, 'form':form})

    else:
        return HttpResponseRedirect('/accounts/login/')


def edit_profile_purpose(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.user.is_superuser == True:
                form1 = EditUserProfileForm(request.POST, instance = request.user)
                form2 = EditUserAddressForm(request.POST, instance = request.user.address)
            else:
                form1 = EditUserProfileForm(request.POST, instance = request.user)
                form2 = EditUserAddressForm(request.POST, instance=request.user.address)
            if form1.is_valid:
                messages.success(request, 'Profile Updated!')
                form1.save()
            if form2.is_valid:
                messages.success(request, 'Profile Updated!')
                form2.save()
        else:
            if request.user.is_superuser == True:
                form1 = EditUserProfileForm(instance=request.user)
                form2 = EditUserAddressForm(instance=request.user.address)
            else:
                form1 = EditUserProfileForm(instance=request.user)
                form2 = EditUserAddressForm(instance=request.user.address)
        return render(request, 'accounts/edit_user_profile.html', {'name':request.user, 'form1': form1, 'form2':form2})

    else:
        return HttpResponseRedirect('accounts/login/')


def change_password(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PasswordChangeForm(user=request.user, data=request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                return render(request, 'accounts/user_profile.html')
        else:
            form = PasswordChangeForm(user=request.user)
        return render(request, 'accounts/changepass.html', {'form': form})
    else:
        return HttpResponseRedirect('/login/')


def send_email_after_registration(email, token, acc):
    account_no = acc
    subject = "Verify Email"
    message = f'Hi, This {account_no} is your account number. Clink on the link to activate your account http://127.0.0.1:8000/accounts/verify/{token}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject=subject,message=message,from_email=from_email,
              recipient_list=recipient_list)



def account_verify(request, token):
    pf= Profile.objects.filter(token=token).first()
    if request.method == 'POST':
        form = AccountPinForm(request.POST)
        if form.is_valid():
            pf.verify = True
            pin = form.cleaned_data.get('pin')
            pf.pin = pin
            pf.save()
        messages.success(request, "Account Pin Saved.")
        return redirect('/accounts/login/')
    else:
        form = AccountPinForm()

    messages.success(request, "Your account has been verified. Please set your account pin number.")
    return render(request, 'accounts/account_pin.html', {'form':form})


