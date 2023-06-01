"""
Database models.
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)

from djmoney.models.fields import MoneyField
from django.utils.translation import gettext_lazy as _
from django.core.validators import (RegexValidator, MinValueValidator, MaxValueValidator)

from decimal import Decimal


class TimeStampedModel(models.Model):
    """Model base class to add on records, created and updated autopopulated datetime fields."""

    created_at = models.DateTimeField(auto_now_add=True)  # editable = false
    updated_at = models.DateTimeField(auto_now=True)  # editable = false


class MerchantCategoryCode(models.Model):
    """Merchant Category Code (MCC) object."""

    mcc = models.PositiveIntegerField()
    edited_description = models.CharField(max_length=255)
    combined_description = models.CharField(max_length=255)
    usda_description = models.CharField(max_length=255)
    irs_description = models.CharField(max_length=255)

    class Meta:
        verbose_name = "merchant category code (mcc)"
        verbose_name_plural = "merchant category codes (mcc)"

    def __str__(self):
        return f'{self.irs_description} ({self.mcc})'


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None):
        """Create, save and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    # replace default user model username to email
    USERNAME_FIELD = 'email'


class PaymentCard(TimeStampedModel):
    "Payment Card object."

    class CardType(models.TextChoices):
        INTERAC = 'Interac', _('Interac')
        MASTERCARD = 'Mastercard', _('Mastercard')
        VISA = 'Visa', _('Visa')
        AMEX = 'Amex', _('Amex')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    card_type = models.CharField(max_length=25, choices=CardType.choices)
    four_digits = models.PositiveIntegerField(
        validators=[MinValueValidator(0000, 'Must be 4 digits.'),
                    MaxValueValidator(9999, 'Must be 4 digits.')])

    def __str__(self):
        return f'{self.name} ({self.card_type})'


class TransactionUserCategory(TimeStampedModel):
    """Transaction Category defined by the user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    hexcolor = models.CharField(max_length=7, default='#ffffff', validators=[RegexValidator(
        r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', message='Wrong Hexadecimal color format.')])

    class Meta:
        verbose_name = "user category"
        verbose_name_plural = "user categories"

    def __str__(self):
        return f'{self.name}'


class TransactionMerchant(TimeStampedModel):
    """Merchant added by the user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True)
    default_user_category = models.ForeignKey(TransactionUserCategory, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "merchant"
        verbose_name_plural = "merchants"

    def __str__(self):
        return f'{self.name} ({str(self.location)})'


class CreditCardMerchantCategory(TimeStampedModel):
    """Transaction category defined by credit card networks."""

    class CardRewards(models.TextChoices):
        POINTS = 'Points', _('Points')
        CASHBACK = 'CashBack', _('CashBack')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    credit_card = models.ForeignKey(PaymentCard, on_delete=models.CASCADE)
    merchant = models.ForeignKey(TransactionMerchant, on_delete=models.CASCADE)
    mcc = models.ForeignKey(MerchantCategoryCode, on_delete=models.SET_NULL, null=True)
    cash_back = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(0),
                                    validators=[MinValueValidator(0), MaxValueValidator(100)])
    points_multiplier = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(9)])
    rewards_type = models.CharField(max_length=25, choices=CardRewards.choices, default=CardRewards.CASHBACK)

    class Meta:
        verbose_name = "credit card category"
        verbose_name_plural = "credit card categories"

    def __str__(self):
        return f'{self.credit_card.name} + {self.merchant.name} ({self.mcc.irs_description}) \
            = [{self.cash_back}%, {self.points_multiplier}x]'


class Transaction(TimeStampedModel):
    """Transaction object."""

    class TransactionType(models.TextChoices):
        INCOME = 'Income', _('Income')
        EXPENSE = 'Expense', _('Expense')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    payment_card = models.ForeignKey(PaymentCard, on_delete=models.SET_NULL,
                                     null=True, blank=True)  # null if parent exists
    user_category = models.ForeignKey(TransactionUserCategory, on_delete=models.SET_NULL,
                                      null=True, blank=True)  # null if parent exists
    merchant = models.ForeignKey(TransactionMerchant, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=25, choices=TransactionType.choices, default=TransactionType.EXPENSE)
    amount = MoneyField(max_digits=10, decimal_places=2, default=0, default_currency='CAD')
    authorized_date = models.DateField()
    details = models.TextField(blank=True)

    def __str__(self):
        return f'{self.merchant.name} ({str(Decimal(self.amount.amount))})'
