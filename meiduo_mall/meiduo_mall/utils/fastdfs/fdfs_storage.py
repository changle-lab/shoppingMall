from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from fdfs_client.client import Fdfs_client

@deconstructible
class FastDFSStorage(Storage):
    def __init__(self, client_conf=None, base_url=None):
        if client_conf is None:
            client_conf = settings.CLIENT_CONF

        self.client_conf = client_conf

        if base_url is None:
            base_url = settings.BASE_URL

        self.base_url = base_url

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_length=None):
        c = Fdfs_client(self.client_conf)

        status = c.upload_by_buffer(content.read())

        # 判断是否上传成功.
        if status['Status'] != 'Upload successed.':
            raise Exception('upload errors')

        file_id=status['Remote file_id']

        return file_id

    def url(self, name):

        return self.base_url+name

    def exists(self, name):

        return False