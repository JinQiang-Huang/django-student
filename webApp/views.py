from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Users
from django.core.paginator import Paginator

# Create your views here.

# decorator cookie


def cookie_auth(func):
    def inner(request, *args, **kwargs):
        cookie_value = request.COOKIES.get('username')
        if not cookie_value:
            return redirect('login')
        return func(request, *args, **kwargs)
    return inner

# decorator session


def session_auth(func):
    def inner(request, *args, **kwargs):
        session_value = request.session.get('username')
        if not session_value:
            return redirect('login')
        return func(request, *args, **kwargs)
    return inner


def login(request):
    user_li = Users.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')

        result = []
        for user in user_li:
            if (user.name == name or user.email == name) and user.password == password:
                result.append('success')
            else:
                result.append('failed')

        if 'success' in result:
            if '@' not in name:
                user_message = Users.objects.filter(name=name).values()[0]
            else:
                user_message = Users.objects.filter(email=name).values()[0]

            admin_email = Users.objects.filter(name='admin').values()[0]
            if name == 'admin' or name == admin_email.get('email'):
                rep = redirect('users')
                # cookie
                # rep.set_cookie('username', name, expires=10)

                # session
                request.session['username'] = name
                # request.session.set_expiry(10)

                return rep
            else:
                rep = render(request, 'detail.html', user_message)
                # cookie
                # rep.set_cookie('username', name, expires=5)

                # session
                request.session['username'] = name
                # request.session.set_expiry(10)

                return rep
        else:
            return render(request, 'login.html', {'error': '⚠Username or Password is Error.'})

    # logout delete browser record
    request.session.flush()
    return render(request, 'login.html')


# @cookie_auth
@session_auth
def users(request):
    current_page = int(request.GET.get('page_num', 1))
    user_data = Users.objects.all().order_by('id')
    paginator = Paginator(user_data, 10)

    if paginator.num_pages > 11:
        if current_page - 5 < 1:
            page_range = range(1, 12)
        elif current_page + 5 > paginator.num_pages:
            page_range = range(paginator.num_pages - 10,
                               paginator.num_pages + 1)
        else:
            page_range = range(current_page - 5, current_page + 5)
    else:
        page_range = paginator.page_range

    try:
        page = paginator.page(current_page)
    except Exception as E:
        current_page = 1
        page = paginator.page(current_page)

    result = {"page_range": page_range, 'page': page,
              'current_page': current_page, 'count_page': paginator.num_pages, "title": "Users List"}
    return render(request, 'users.html', result)


# @cookie_auth
@session_auth
def create(request):
    # for i in range(1,151):
    #   Users.objects.create(name='user{}'.format(i),email='user{}@wsc.org'.format(i),password='user{}'.format(i))

    # user = Users.objects.get(name='user'+str(i))
    # user.delete()

    user_li = Users.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        for user in user_li:
            if user.name == name or user.email == email:
                return render(request, 'create.html', {'error': '⚠Username or Password is Exist.'})

        user_data = Users(name=name, email=email, password=password)
        user_data.save()
        return redirect('users')
    return render(request, 'create.html')


# @cookie_auth
@session_auth
def detail(request, id):
    user = Users.objects.filter(id=id).values()[0]
    return render(request, 'detail.html', user)


# @cookie_auth
@session_auth
def edit(request, id):
    user_data = Users.objects.filter(id=id).values()[0]
    user_modify = Users.objects.get(id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_modify.name = name
        user_modify.email = email
        user_modify.password = password
        user_modify.save()
        return redirect('users')
    return render(request, 'edit.html', user_data)


# @cookie_auth
@session_auth
def delete(request, id):
    user = Users.objects.get(id=id)

    if user.name == 'admin':
        user_data = Users.objects.all()
        result = {"user_data": user_data, "title": "Users List",
                  "error": "⚠Admin user can\'t delete."}
        return render(request, 'users.html', result)

    user.delete()
    return redirect('users')


def del_cookie(request):
    rep = HttpResponse('Delete Cookie Successful.')
    rep.delete_cookie('username')
    return rep


def del_session(request):
    rep = HttpResponse('Delete Session Successful.')
    request.session.flush()
    return rep
