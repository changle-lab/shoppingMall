from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.filters import OrderingFilter

from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.
from goods.models import GoodsCategory, SKU
from goods.serializers import SKUSerializers, SKUSearchSerializer, SKUHistorySerializer
from goods.utils import PageNum
from drf_haystack.viewsets import HaystackViewSet

class CategoriesView(APIView):
    """
        面包屑导航分类数据获取
    """
    def get(self, request, pk):
        #获取前端数据

        #通过三级分类查询二级分类
        cat3 = GoodsCategory.objects.get(id=pk)

        #通过二级分类查询一级分类
        cat2 = cat3.parent

        #返回三个分类对象
        cat1= cat2.parent

        return Response({
            'cat1': cat1.name,
            'cat2': cat2.name,
            'cat3': cat3.name
        })


class SKUSView(ListAPIView):

    serializer_class = SKUSerializers
    # queryset =

    pagination_class = PageNum
    #制定过滤器类
    filter_backends = [OrderingFilter]   #过滤排序
    #制定过滤起字段
    ordering_fields = ('create_time', 'sales', 'price')

    def get_queryset(self):
        pk = self.kwargs['pk']
        return SKU.objects.filter(category_id=pk)

    # def get(self, request, pk):
    #     #获取分类id
    #     查询类分id的多有对象
    #     序列化返回, 分页,过滤排序

class SKUSearchView(HaystackViewSet):

    index_models = [SKU]

    serializer_class = SKUSearchSerializer

    pagination_class = PageNum

class SKUHistoryView(CreateAPIView, ListAPIView):
    """
        用户浏览记录
    """
    serializer_class = SKUHistorySerializer

    #需要id才能获取到浏览的记录,但是这里没办法获取到缓存里存的id
    #获取不到缓存里的id,因为么办法获取到用户信息,77行
    queryset = SKU.objects.filter()

    def get_queryset(self):
        #获取用户
        user = self.request.user
        #建立缓存链接
        conn = get_redis_connection('history')
        #查询缓存数据获取到sku_id
        sku_ids = conn.lrange("history_%s" % user.id, 0,100)
        # 根据id查询商品对象
        skus = SKU.objects.filter(id__in=sku_ids)
        # 序列化返回商品
        return skus

    def get_serializer_class(self):
        # 请求不同,使用序列化器不同
        if self.request.method == 'POST':
            return SKUHistorySerializer

        else:
            return SKUSerializers
