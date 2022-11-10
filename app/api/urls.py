from .views import UserViewSet, CategoryViewSet, TransactionViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = router.urls
