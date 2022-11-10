import collections
from datetime import datetime, timedelta
from django.core.management import BaseCommand
from django.db.models import Sum, Case, When, F, IntegerField
from django.db.models.functions import Coalesce
from django.utils import timezone

from api.models import CUser, Transaction


class Command(BaseCommand):
    help = 'Send emails every day'

    def handle(self, *args, **options):
        format_date = '%d.%m.%Y'

        users = CUser.objects.exclude(email=None).values('email', 'id').all()

        transactions = Transaction.objects.filter(date__gte=timezone.now() - timedelta(days=7)).values('user', 'date__date').annotate(
            amount=Coalesce(Sum(
                Case(
                    When(direction=1, then=F('amount')),
                    default=(F('amount') * -1),
                    output_field=IntegerField()
                )), 0
            ))
        result = {}
        for trans in transactions:
            user = trans['user']
            t_date = trans['date__date'].strftime(format_date)
            amount = trans['amount']
            if result.get(user):
                if result[user].get(t_date):
                    result[user][t_date] = result[user][t_date] + amount
                else:
                    result[user][t_date] = amount
            else:
                result[user] = {}
                result[user][t_date] = amount
        for user in users:
            if result.get(user['id']):
                user_items = result[user['id']]
                ordered = collections.OrderedDict(
                    sorted(user_items.items(), key=lambda x: datetime.strptime(x[0], '%d.%m.%Y'))
                )
                message = f'Посуточная статистика пользователя {user["email"]} на 7 дней:\n'
                for item in ordered.items():
                    message += f'{item[0]}: {item[1]}р\n'
                print(message)
        self.stdout.write(self.style.SUCCESS('Successfully poll'))
