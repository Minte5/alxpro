from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth


#Customer Registration
def register(request):
    if request.POST:
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username is already taken.')
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'email is already registered.')
                return redirect('signup')
            else:
                pwd = make_password(password)
                user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=pwd)
                user.save()
                messages.success(request,'you have been registered successfully.')
                return redirect('signin')
        else:
            messages.error(request,"Sorry, Password Don't match")
            return redirect('signup')
    if not request.POST:
        return render(request, 'signup.html')
    
@csrf_exempt
def login(request):
    # sourcery skip: last-if-guard, merge-else-if-into-elif, swap-if-else-branches
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        user=User.objects.get(username=username)
        if user is not None:
            if check_password(password=password, encoded=make_password(password), setter=None):
                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('store')
            else:
                messages.error(request, 'Sorry, your password isn\'t correct')
                return redirect('signin')
        else:
            messages.error(request,'Username doesn\'t exist. Please try again.')
            return redirect('signin')
    else:
        return render(request, 'signin.html')
    
def logout(request):
    username = request.user.username
    user = User.objects.get(username=username)
    auth.logout(request)
    request.session.clear()
    return redirect('signin')
    
@login_required    
def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)