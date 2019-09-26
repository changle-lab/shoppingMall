from django.shortcuts import render
# Create your views here.

from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.response import Response

from areas.models import Area
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from areas.serializers import AreasSerializer, AddressSerializer
from users.models import Address


class GetAreasView(CacheResponseMixin, ListAPIView):
    """
        获取所有省的信息
    """
    serializer_class = AreasSerializer
    queryset = Area.objects.filter(parent=None)


class GetAreaView(CacheResponseMixin, ListAPIView):
    """
        获取所有省的信息
    """
    serializer_class = AreasSerializer

    queryset = Area.objects.filter(parent_id=None)

    def get_queryset(self):
        pk = self.kwargs['pk']

        return Area.objects.filter(parent_id=pk)


class AddressView(CreateAPIView, UpdateAPIView, ListAPIView):
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_deleted=False)

    def delete(self, request, pk):
        obj = self.get_object()
        obj.is_deleted = True
        obj.save()

        return Response()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'addresses': serializer.data, 'default_address_id':self.request.user.default_address_id})
