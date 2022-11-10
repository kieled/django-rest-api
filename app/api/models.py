from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models

from api.managers import CustomUserManager

default_categories = [
    "Забота о себе", "Зарплата", "Здоровье и фитнес",
    "Кафе и рестораны", "Машина", "Образование",
    "Отдых и развлечения", "Платежи, комиссии", "Покупки: одежда, техника",
    "Продукты", "Проезд"
]


class Category(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey('CUser', on_delete=models.CASCADE, related_name='categories')


class CUser(AbstractUser):
    first_name = None
    last_name = None
    groups = None
    user_permissions = None

    email = models.EmailField("email address", blank=False, unique=True)

    balance = models.IntegerField(default=0)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def create_categories(self):
        for category in default_categories:
            category = Category(name=category, user=self)
            category.save()


class Transaction(models.Model):
    DIRECTION_ENUM = (
        (1, 'Up'),
        (2, 'Down')
    )

    direction = models.IntegerField(choices=DIRECTION_ENUM)
    amount = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)
    organization = models.CharField(max_length=200)
    description = models.TextField(max_length=500, null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(CUser, on_delete=models.CASCADE)
