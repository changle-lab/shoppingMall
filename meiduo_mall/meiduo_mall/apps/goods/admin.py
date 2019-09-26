from django.contrib import admin
from goods import models
# Register your models here.
# from goods.utils import generate_static_list_search_html
from celery_tasks.static_html.tasks import generate_static_list_search_html, generate_static_sku_detail_html

class GoodsModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'sales')

    def save_model(self, request, obj, form, change):
        generate_static_list_search_html.delay()


class SKUModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()

        generate_static_sku_detail_html.delay(obj.id)

    def delete_model(self, request, obj):

        obj.delete()
        generate_static_sku_detail_html.delay(obj.id)


admin.site.register(models.Goods, GoodsModelAdmin)
admin.site.register(models.SKU, SKUModelAdmin)
admin.site.register(models.SKUImage)
