from django.urls import path

from . import views

urlpatterns = [
	#Leave as empty string for base url
	path('store/', views.store, name="store"),
 	path('', views.login, name="signin"),
 	path('signup/', views.register, name="signup"),
	path('signout/', views.register, name="signout"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),

]