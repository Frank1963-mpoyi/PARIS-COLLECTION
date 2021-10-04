import json
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render

from store.models import Order, Product, OrderItem, ShippingAddress
from store.utils import cookieCart, carData


def store(request):
    template_name = 'store/index.html'

    data = carData(request)

    cartItems = data['cartItems']
    # order = data['order']
    # items = data['items']

    products = Product.objects.all().order_by("title")

    context = {'products': products, 'cartItems': cartItems}

    return render(request, template_name, context)



def cart(request):
    template_name = 'store/cart.html'

    data = carData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems':cartItems}

    return render(request, template_name, context)


#@csrf_exempt
def updateitem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('product json ',productId, 'action',action)

    user = request.user

    product = Product.objects.get(id=productId)

    order, created = Order.objects.get_or_create(user=user, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)# if it already exist we want to change the value not create a new one

    if action == 'add':
        orderItem.quantity = (orderItem.quantity +1)
    elif action == 'remove':
        orderItem.quantity -= 1

    if action == 'delete':
        orderItem.delete()

    orderItem.save()

    if  orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)




def checkout(request):
    template_name = 'store/checkout.html'

    data = carData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems':cartItems}

    return render(request, template_name, context)


def processOrder(request):
    #print("data:", request.body)
    transaction_id = datetime.datetime.now().timestamp()

    data = json.loads(request.body)

    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, complete=False)

        total = float(data['form']['total'])# we need to get form value in body we stringify   body:JSON.stringify({ 'form':userFormData, 'shipping':shippingInfo})

        order.transaction_id = transaction_id

        if total == order.get_cart_total: # if the front end total == backend total / may be intruder can manipulate the total in front end
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(

                user        =user,
                order       = order,
                address     =data['shipping']['address'],
                city        =data['shipping']['city'],
                state       =data['shipping']['state'],
                zipcode     =data['shipping']['zipcode'],
                #date_added =data[''][''],
            )

    else:
        pass


    return JsonResponse("Payment submitted....", safe=False)