from django.shortcuts import render
from django.shortcuts import redirect
from . import models, forms
import hashlib
import datetime
import pytz
from Demo001 import settings
from django.shortcuts import HttpResponse
# from .tasks import add
# Create your views here.


def make_confirm_string(user):
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	code = hash_code(user.name, now)
	models.ConfirmString.objects.create(code=code, user=user,)

	return code


def send_email(email, code):

	from django.core.mail import EmailMultiAlternatives

	subject = '来自http://127.0.0.1:8000/的测试邮件'

	text_content = '''欢迎访问http://127.0.0.1:8000，这里是听风留的博客和测试站点。'''

	html_content = '''
<p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>http://127.0.0.1:8000</a>，\
这里是听风留的博客和教程站点，专注于Python和Django技术的分享！</p>
<p>请点击站点链接完成注册确认！</p>
<p>此链接有效期为{}天！</p>
'''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

	msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
	msg.attach_alternative(html_content, "text/html")
	msg.send()


def index(request):
	pass
	return render(request, 'login/index.html')


def login(request):
	if request.session.get('is_login', None):
		redirect('/index/')
	if request.method == "POST":
		login_form = forms.UserForm(request.POST)
		message = "请检查填写的内容！"
		if login_form.is_valid():
			username = login_form.cleaned_data['username']
			password = login_form.cleaned_data['password']
			try:
				user = models.User.objects.get(name=username)
				if not user.has_confirmed:
					message = "该用户还未通过邮件确认！"
					return render(request, 'login/login.html', locals())
				if user.password == hash_code(password):
					request.session['is_login'] = True
					request.session['user_id'] = user.id
					request.session['user_name'] = user.name
					return redirect('/index/')
				else:
					message = "密码不正确！"
			except:
				message = "用户名未注册！"
		return render(request, 'login/login.html', locals())
	login_form = forms.UserForm()
	return render(request, 'login/login.html', locals())


def register(request):
	if request.session.get('is_login', None):
		redirect('/index/')
	if request.method == "POST":
		register_form = forms.RegisterForm(request.POST)
		message = "请检查填写的内容！"
		if register_form.is_valid():
			username = register_form.cleaned_data['username']
			password1 = register_form.cleaned_data['password1']
			password2 = register_form.cleaned_data['password2']
			email = register_form.cleaned_data['email']
			sex = register_form.cleaned_data['sex']
			if password1 != password2:
				message = "两次输入的密码不同！"
				return render(request, 'login/register.html', locals())
			else:
				same_name_user = models.User.objects.filter(name=username)
				if same_name_user:
					message = '用户已存在，请重新选择用户名！'
					return render(request, 'login/register.html', locals())
				same_email_user = models.User.objects.filter(email=email)
				if same_email_user:
					message = '该邮箱已注册，请使用别的邮箱！'
					return render(request, 'login/register.html', locals())

				new_user = models.User()
				new_user.name = username
				new_user.password = hash_code(password1)
				new_user.email = email
				new_user.sex = sex
				new_user.save()

				code = make_confirm_string(new_user)
				send_email(email, code)

				return redirect('/login/')
	register_form = forms.RegisterForm()
	return render(request, 'login/register.html', locals())


def logout(request):
	if not request.session.get('is_login', None):
		return redirect('/index/')
	request.session.flush()

	return redirect('/index/')


def hash_code(s, salt='Demo001'):
	h = hashlib.sha256()
	s += salt
	h.update(s.encode())
	return h.hexdigest()


def user_confirm(request):
	code = request.GET.get('code', None)
	message = ''
	try:
		confirm = models.ConfirmString.objects.get(code=code)
	except:
		message = '<font color="red">无效的确认请求！</font>'
		return render(request, 'login/confirm.html', locals())
# http://127.0.0.1:8000/confirm/?code=2447bbc45aa375f79be8d86e9385a9771321929243817a29bba503fbb9663a10
	c_time = confirm.c_time
	now = datetime.datetime.now()
	print(now)
	now = now.replace(tzinfo=pytz.timezone('UTC'))
	print(now)
	print(c_time)
	if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
		confirm.user.delete()
		message = '<font color="yellow">您的邮箱已经过期！请重新注册</font>'
		return render(request, 'login/confirm.html', locals())
	else:
		confirm.user.has_confirmed = True
		confirm.user.save()
		confirm.delete()
		message = '<font color="greenyellow">谢谢使用    请使用账号登陆</font>'

		return render(request, 'login/confirm.html', locals())

