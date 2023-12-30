-pip install django djangorestframework


-django-admin startproject your_project_name
cd your_project_name


-python manage.py startapp products


-# products/models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    retrieval_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


-# products/serializers.py
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


-# products/views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.utils import timezone
from django.db.models import Count

from .models import Product
from .serializers import ProductSerializer

@api_view(['GET'])
def top_products(request, period):
    """
    Retrieve the top 5 products based on the retrieval count.
    
    Parameters:
    - period: 'all', 'last_day', or 'last_week'
    """
    if period == 'all':
        products = Product.objects.annotate(retrieval_count=Count('retrieval_date')).order_by('-retrieval_count')[:5]
    elif period == 'last_day':
        start_date = timezone.now() - timezone.timedelta(days=1)
        products = Product.objects.filter(retrieval_date__gte=start_date).annotate(retrieval_count=Count('retrieval_date')).order_by('-retrieval_count')[:5]
    elif period == 'last_week':
        start_date = timezone.now() - timezone.timedelta(weeks=1)
        products = Product.objects.filter(retrieval_date__gte=start_date).annotate(retrieval_count=Count('retrieval_date')).order_by('-retrieval_count')[:5]
    else:
        return Response({'error': 'Invalid period parameter'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


-# products/urls.py
from django.urls import path
from .views import ProductList, ProductDetail, top_products

urlpatterns = [
    path('products/', ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('top-products/<str:period>/', top_products, name='top-products'),
]


-# your_project_name/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('products.urls')),
]


-to run and start the server
python manage.py makemigrations
python manage.py migrate
python manage.py runserver