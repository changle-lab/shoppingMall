from celery_tasks.main import app
from libs.yuntongxun.sms import CCP

@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    ccp = CCP()
    ccp.send_template_sms(mobile, [sms_code, 5], 1)