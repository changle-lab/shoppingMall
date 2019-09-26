import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    # 获取cookie
    # 判断cookie是否存在
    cart_cookie = request.COOKIES.get('cart_cookie')
    # 不存在返回django_session
    if cart_cookie is None:
        return response
    # 解密cookie
    cart = pickle.loads(base64.b64decode(cart_cookie))
    # 判断解密后的值是否为空
    if cart is None:
        # 为空返回

        return response
    # 数据拆分
    data = {}
    # 拆分为hash类型    字典
    data_list = []
    # 拆分集合          列表
    data_list_nong = []
    for sku_id, data_dict in cart.items():
        data[sku_id] = data_dict['count']
        if data_dict['selected']:
            data_list.append(sku_id)
        else:
            data_list_nong.append(sku_id)

    # 建立redis链接对象
    conn = get_redis_connection('cart')
    # 写入hash数据中
    conn.hmset('cart_%s' % user.id, data)
    # 写入集合中
    if data_list:
        conn.sadd('cart_selected_%s' % user.id, *data_list)

    if data_list_nong:
        conn.srem('cart_selected_%s' % user.id, *data_list_nong)

    # 删除cookie
    response.delete_cookie('cart_cookie')
    # 返回结果
    return response

