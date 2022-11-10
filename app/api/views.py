from datetime import datetime, timedelta
from django.db.models import Sum, When, Case, IntegerField, F
from django.db.models.functions import Coalesce

from .models import CUser, Category, Transaction
from rest_framework import viewsets, permissions, status, filters, decorators
from rest_framework.generics import mixins
from django_filters import rest_framework
from rest_framework.response import Response
from .serializers import UserSerializer, CategorySerializer, UserCreateSerializer, \
    CreateTransactionSerializer, StatisticPeriodSerializer, StatisticResponseSerializer


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        return CUser.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CUser.objects.create_user(**serializer.validated_data)
        user.create_categories()
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @decorators.action(methods=['get'], detail=False, url_path='self', url_name='get_self')
    def get_self(self, request, *args, **kwargs):
        user = CUser.objects.get(id=request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class TransactionViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['amount']
    search_fields = ['date']
    ordering_fields = ['amount', 'date']

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = CreateTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CUser.objects.get(id=request.user.id)
        serializer.validated_data['user_id'] = user.id
        amount = serializer.validated_data['amount']
        direction = serializer.validated_data['direction']
        if direction == 1:
            user.balance += amount
        else:
            if user.balance <= amount:
                return Response({'status': 'Not enough money'}, status=status.HTTP_400_BAD_REQUEST)
            user.balance -= amount
        serializer.save()
        user.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @decorators.action(methods=['get'], detail=False, url_path='stats', url_name='stats')
    def get_stats(self, request):
        serializer = StatisticPeriodSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        period_days = serializer.validated_data['period']
        base = datetime.today()
        date_list = [base - timedelta(days=x) for x in range(period_days)]
        result = []

        for date in date_list:
            transactions = Transaction.objects.filter(
                date__date=date,
                user_id=self.request.user.id
            ).aggregate(
                amount=Coalesce(Sum(
                    Case(
                        When(direction=1, then=F('amount')),
                        default=(F('amount') * -1),
                        output_field=IntegerField()
                    )), 0
            ))
            result.append({
                'date': date.date(),
                'amount': transactions['amount']
            })

        serializer = StatisticResponseSerializer({'data': result})
        return Response(serializer.data, status=status.HTTP_200_OK)
