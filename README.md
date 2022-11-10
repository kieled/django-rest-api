# DRF API

## Installing

> build and run: `docker compose up -d --build`


>apply db migrations: `docker compose exec web python manage.py migrate`

## Additional info

* `Authorization: Token {access_token}` for use auth


* sending to email functionality not realized, but: 

```
path: /app/api/management/commands/send_mails.py
``` 

* display all prepared info to the console by the command:

```
docker compose exec web python manage.py send_mails
```

## Main Endpoints:

> **GET** `/api/users/self/` - get current user info (balance, username, id)

> **CRUD** `/api/categories/{id | None}` - user categories


> **POST** `/api/users/` - register

```
payload: {
    'email': required Str,
    'password': requered Str,
    'username': required Str
}
```

> **POST** `/api/token/` - get access/refresh tokens

```
payload: {
    'username': required Str,
    'password': required Str
}
```

> **CRUD** `/api/transactions/{id | None}` - user transactions

```
Query params:

    amount=1000, #Filter by amount of transaction
    search='10.02.2022', #Filter by date or time
    order_by= 'amount' | 'date' | '-amount' | '-date'
```

> **GET** `/api/transactions/stats/` - get statistic

```
Query params: 

    period: int (requireed, 0 - 30)
```

