from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, ModelChoiceField, Form, IntegerField
from django_recaptcha.fields import ReCaptchaField

from apps.models import User, Address
from apps.models.order import Order, CreditCard


class UserRegisterModelForm(AuthenticationForm, ModelForm):
    password2 = CharField(max_length=128)
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'email', 'username', 'password', 'password2'

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise ValidationError
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.save()
        return user


class CartAddProductForm(Form):
    quantity = IntegerField(min_value=1, max_value=100)


class OrderCreateModelForm(ModelForm):
    address = ModelChoiceField(queryset=Address.objects.all())
    owner = ModelChoiceField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Order
        fields = 'payment_method', 'address', 'owner'

    def save(self, commit=True):
        obj: Order = super().save(commit)

        if commit and obj.payment_method == 'credit_card':
            cvv = self.data.pop('cvv')
            expire_date = self.data.pop('expire_date')
            number = self.data.pop('number')
            CreditCard.objects.create(
                owner=obj.owner,
                order=obj
                
            )
        return obj
class CreditCardForm(ModelForm):
    class Meta:
        model = CreditCard
        fields = ['expire_date', 'cvv', 'number']

    # class CaptchaTestForm(Form):
    #     myfield = AnyOtherField()
