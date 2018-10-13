import os
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

os.environ['DJANGO_SETTINGS_MODULE'] = 'Demo001.settings'

if __name__ == '__main__':

	subject, from_email = '来自http://127.0.0.1:8000/的测试邮件', 'du2579350910@163.com'
	to = 'du2579350910@163.com'
	text_content = "欢迎访问http://127.0.0.1:8000，这里是听风留的博客和测试站点。"
	html_content = '<p>欢迎访问<a href="http://127.0.0.1:8000" target=blank>http://127.0.0.1:8000</a>，这里是听风留的博客和教程站点</p>'
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
	msg.attach_alternative(html_content, "text/html")
	msg.send()
