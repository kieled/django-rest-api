from rest_framework import serializers

from .models import CUser, Category, Transaction


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CUser
        fields = ['id', 'username', 'balance']


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'date', 'organization', 'description', 'direction', 'category']


class CreateTransactionSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True)
    organization = serializers.CharField(required=True)
    description = serializers.CharField(required=False)
    direction = serializers.ChoiceField(choices=[(1, 'up'), (2, 'down')])
    category_id = serializers.IntegerField(required=True)

    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)


class StatisticPeriodSerializer(serializers.Serializer):
    period = serializers.IntegerField(max_value=30, required=True)


class StatisticItemSerializer(serializers.Serializer):
    date = serializers.DateField(read_only=True)
    amount = serializers.IntegerField(read_only=True)

class StatisticResponseSerializer(serializers.Serializer):
    data = StatisticItemSerializer(many=True)