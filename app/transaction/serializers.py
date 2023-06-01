"""
Serializers for Transaction APIs
"""
from rest_framework import serializers

from core.models import Transaction, TransactionMerchant, TransactionUserCategory, \
    PaymentCard, MerchantCategoryCode, CreditCardMerchantCategory


class MerchantCategoryCode(serializers.ModelSerializer):
    """Serializer for Merchant categories codes."""

    class Meta:
        model = MerchantCategoryCode
        fields = ['id', 'mcc', 'edited_description', 'combined_description',
                  'usda_description', 'irs_description', 'created_at', 'updated_at']
        read_only_fields = ['id']


class PaymentCardSerializer(serializers.ModelSerializer):
    """Serializer for payment cards."""

    class Meta:
        model = PaymentCard
        fields = ['id', 'name', 'card_type', 'four_digits', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransactionUserCategorySerializer(serializers.ModelSerializer):
    """Serializer for user transactions categories."""

    class Meta:
        model = TransactionUserCategory
        fields = ['id', 'name', 'hexcolor', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransactionMerchantSerializer(serializers.ModelSerializer):
    """Serializer for merchants."""

    class Meta:
        model = TransactionMerchant
        fields = ['id', 'name', 'location', 'default_user_category', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreditCardMerchantCategorySerializer(serializers.ModelSerializer):
    """Serializer for relationship between merchants and network rewards mcc categories."""

    class Meta:
        model = CreditCardMerchantCategory
        fields = ['id', 'credit_card', 'merchant', 'mcc', 'cash_back',
                  'points_multiplier', 'rewards_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transactions."""

    class Meta:
        model = Transaction
        fields = ['id', 'parent', 'payment_card', 'user_category', 'merchant',
                  'type', 'amount', 'authorized_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def _get_or_create_merchant(self, merchant, transaction):
        """Handle get or creating merchant if not existing."""
        auth_user = self.context['request'].user  # get authenticated user
        merchant_obj = TransactionMerchant.objects.get_or_create(user=auth_user, **merchant)
        transaction.merchant = merchant_obj

    def create(self, validated_data):
        """Override Create a Transaction."""
        merchant = validated_data.pop('merchant', None)
        transaction = Transaction.objects.create(**validated_data)
        self._get_or_create_merchant(merchant, transaction)

        return transaction

    def update(self, instance, validated_data):
        """Override Update a Transaction."""
        merchant = validated_data.pop('merchant', None)
        if merchant is not None:
            instance.merchant = None
            self._get_or_create_merchant(merchant, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class TransactionDetailSerializer(TransactionSerializer):
    """Serializer for transaction detail view."""

    class Meta(TransactionSerializer.Meta):
        fields = TransactionSerializer.Meta.fields + ['details']
