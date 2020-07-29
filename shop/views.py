from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact, Order, OrderUpdate
from math import ceil
import json
from django.contrib import messages

# Create your views here.
def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)

def searchMatch(query, item):
    #Return true if only query matches the item
    query = query.lower()
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.subcategory.lower() or query in item.category.lower():
        return True
    else:
        return False
def search(request):
    query = request.GET.get('search')
    print(query)
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query,item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if n != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds, 'msg':""}
    if len(allProds) == 0:
        params = {'msg': "No search result found."}
    return render(request, 'shop/search.html', params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        if len(name) <= 2 or len(email) <= 4 or len(phone) < 10 or len(desc) < 4:
            messages.error(request, "Please fill the form correctly")
        else:
            contact = Contact(name=name, email=email, phone=phone, desc=desc)
            contact.save()
            messages.success(request, "Your form has been submitted")
    return render(request, 'shop/contact.html')

def tracker(request):
    if request.method == 'POST':
        order_id = request.POST.get('orderId')
        email = request.POST.get('email')
        try:
            order = Order.objects.filter(order_id=order_id, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=order_id)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time':item.timestamp})
                    response = json.dumps({'status':'success', 'updates':updates, 'itemsJson':order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')
    return render(request, 'shop/tracker.html')


def productView(request, myid):
    products = Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html', {'product':products[0]})

def checkout(request):
    if request.method == 'POST':
        items_Json = request.POST.get('itemsJson')
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address1') + ' ' + request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip')
        phone = request.POST.get('phone')
        order = Order(items_json=items_Json, name=name, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="Your Order has been Placed.")
        update.save()
        thank = True
        id = order.order_id
        return render(request, 'shop/checkout.html', {'thank':thank, 'id':id})
    return render(request, 'shop/checkout.html')