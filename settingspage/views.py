from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.views import View
from django.forms import formset_factory
from django.forms import modelformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from homepage.models import *
from .forms import *
from django.http import JsonResponse
import json
from .urls import *
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from datetime import datetime
from func.func import *

from collections import OrderedDict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


ImageUploadFormSet = modelformset_factory(Image, CreateImgForm, extra=0, can_delete=True)


# Create your views here.
def settingsPage(request):
    return redirect('settingspage:gerenalPage')



#####-------- Sản phẩm -------######
# ProductPage
def ProductManager(request):
    acc = Account.objects.get(user_ptr=request.user)
    user = Sharer.objects.get(account= acc) if acc.role == 'sharer' else Manager.objects.get(account= acc)
    context = {
        'acc' : acc,
        'user' : user
    }
    return render(request, 'products/product.html', context)
#Tạo sản phẩm mới
class CreateProduct(View):
    def get(self, request):
        form_product = ProductForm()
        acc = Account.objects.get(user_ptr=request.user)
        context = {
            'acc' : acc,
            'form_product':form_product
        }
        return render(request, 'products/addproduct.html', context)
    def post(self, request):
        acc = Account.objects.get(user_ptr=request.user)
        if acc.role == 'sharer':
            return HttpResponse("Bạn cần là người quản lý để thực hiện")
        else:
            user = Manager.objects.get(account = acc)
            newProduct = Product.objects.create(provider = user)
            form_product = ProductForm(request.POST, request.FILES, instance= newProduct)
            if form_product.is_valid():
                if form_product.cleaned_data['img'].name == 'default.jpg':
                    messages.error(request, "Thêm sản phẩm thất bại vì thiếu hình ảnh")
                    newProduct.delete()
                    return redirect('settingspage:product')
                product = form_product.save(commit= False) # Đối tượng mô hình k đưa vào cơ sở dữ liệu
                product.save()
                messages.success(request, "Thêm sản phẩm thành công")
            else:
                newProduct.delete()
                messages.error(request, "Thêm sản phẩm thất bại")
            return redirect('settingspage:product')


#Xóa Sản phẩm
def deleteProduct(request, product_id):
    try:
        product = Product.objects.get(pk = product_id)
        product.delete()
        messages.success(request, "Đã xóa sản phẩm")
    except:
        messages.error(request, "Thao tác lỗi")
    return redirect('settingspage:product')

# Sửa sản phẩm
class editProduct(View):
    def get(self, request, product_id):
        acc = Account.objects.get(user_ptr=request.user)
        user = Sharer.objects.get(account= acc) if acc.role == 'sharer' else Manager.objects.get(account= acc)
        _product = Product.objects.get(pk = product_id)
        pform = ProductForm(instance= _product)
        context = {
            'form_product': pform,
            'acc': acc,
        }
        return render(request, 'products/addproduct.html', context)
    def post(self, request, product_id):
        _product = Product.objects.get(pk = product_id)
        pform = ProductForm(request.POST, request.FILES, instance = _product)
        if pform.is_valid():
            pform.save()
            messages.success(request, "Đã lưu thay đổi")
        else :
            messages.error(request, "Thực hiện bị lỗi")
        return redirect('settingspage:product')

#generalPage
def generalPage(request):
    acc = Account.objects.get(user_ptr=request.user)
    user = Sharer.objects.get(account= acc) if acc.role == 'sharer' else Manager.objects.get(account= acc)

    if request.method == 'POST':
        if acc.role == 'sharer':
            user.name = request.POST.get('name')
            user.age = request.POST.get('age')
            user.bio = request.POST.get('comment')

            city_id = request.POST.get('city')
            district_id = request.POST.get('district')
            ward_id = request.POST.get('ward')

            user.city, user.district, user.ward = getArea(city_id, district_id, ward_id)

            if 'avatar' in request.FILES:
                user.avatar = request.FILES.get('avatar')
            user.save()
            context = {
                'role': acc.role,
                'acc': acc,
                'user': user,
            }

            return render(request, 'general/general.html', context)
        else:
            user.name = request.POST.get('name')
            user.phone = request.POST.get('phone')
            user.address = request.POST.get('address')
            user.bio = request.POST.get('comment')
            user.t_open = request.POST.get('t_open')
            user.t_closed = request.POST.get('t_closed')

            city_id = request.POST.get('city')
            district_id = request.POST.get('district')
            ward_id = request.POST.get('ward')

            user.city, user.district, user.ward = getArea(city_id, district_id, ward_id)
            if 'avatar' in request.FILES:
                user.avatar = request.FILES.get('avatar')
            if 'bank' in request.FILES:
                user.bank = request.FILES.get('bank')
            user.facebook_link = request.POST.get('facebook_link')
            user.website_link = request.POST.get('website_link')
            user.save()
            context = {
                'role': acc.role,
                'acc': acc,
                'user': user,
                'time_open': user.t_open,
                'time_close': user.t_closed,
            }

            return render(request, 'general/general.html', context)
    if acc.role == 'manager':   
        time_open = user.t_open.strftime("%H:%M")
        time_close = user.t_closed.strftime("%H:%M")

        context = {
            'role': acc.role,
            'acc': acc,
            'user': user,
            'time_open': time_open,
            'time_close': time_close,
        }
    else:
        context = {
            'role': acc.role,
            'acc': acc,
            'user': user,
        }
    return render(request, 'general/general.html', context)

#Bill Page
def billsPage(request):
   
    acc = Account.objects.get(user_ptr=request.user)
    user = Sharer.objects.get(account= acc) if acc.role == 'sharer' else Manager.objects.get(account= acc)
    bills = user.bill_set.all()
    # Cập nhật trạng thái thanh toán nếu quá hạn
    for bill in bills:
        if not bill.img and (timezone.now() - bill.time).total_seconds() > 600:
            bill.status = "Timeout"
            bill.save()
    selected_data = request.GET.get('selectedData', 'Waiting')
    context = {
        "bills" : bills,
        "acc" : acc,
        "user" : user,
        "data_from_js" : selected_data,
    }
    return render(request, "bills/bills.html", context)

def viewBill(request, billId):
    if request.method == 'GET' :
        bill = Bill.objects.get(id = billId)
        user = Sharer.objects.get(account_id=bill.acc_id) if bill.acc.role=='sharer' else Manager.objects.get(account_id=bill.acc_id) 
        return render(request, "bills/bill.html", {"bill" : bill, 'user': user})
    
def accept(request, billId):
    try :
        bill = Bill.objects.get(pk = billId)
        bill.status = "Accept"
        bill.save()
        # bill.delete()
        messages.success(message='Accept', request=request)
        return redirect('settingspage:billsPage')
    except :
        messages.success(message='Error happened, try again', request=request)
        return redirect('settingspage:billsPage')
def decline(request,billId):
    try :
        bill = Bill.objects.get(pk = billId)
        bill.status = "Decline"
        bill.save()
        # bill.delete()
        messages.success(message='Decline', request=request)
        return redirect('settingspage:billsPage')
    except :
        messages.success(message='Error happened, try again', request=request)
        return redirect('settingspage:billsPage')


    

# postPage
def testPostPage(request):
    acc = Account.objects.get(user_ptr=request.user)
    postList = acc.post_set.all()
    context = {
        'acc': acc,
        'postList': postList,
    }
    return render(request, 'posts/postList.html', context)

def testEditPost(request, postId):
    acc = Account.objects.get(user_ptr=request.user)
    user = Sharer.objects.get(account=acc) if acc.role=='sharer' else Manager.objects.get(account=acc) 
    if request.method == 'GET':
        post = Post.objects.get(id=postId)
        img = post.image_set.all()
        form_img = []
        a = 0
        for i in img :
            a = a + 1
            form_img.append(CreateImgForm(instance=i, prefix=f'form-{a}'))
        context = {
            'user': user,
            'post': post,
            'img': img,
            'form_img': form_img,
            'provider': Manager.objects.all()
        }
        return render(request, 'posts/edit_post.html', context)
    elif request.method == 'POST':
        post = Post.objects.get(id=postId)
        post.title = request.POST.get('title_post')
        post.content = request.POST.get('content_post')
        if request.POST.get('provider_post') != 'None':
            post.provider_id = request.POST.get('provider_post')
        else:
            post.provider_id = None
        img = post.image_set.all()
        form_img = []
        
        a = 0
        for i in img :
            a = a+1
            if i.isDelete == True :
                i.delete()
            else :
                form_img.append(CreateImgForm(request.POST, request.FILES, prefix=f'form-{a}', instance=i))
        for form in form_img:
            form.save()
        images = request.FILES.getlist('images')
        for image in images :
            img = Image.objects.create(post = post, img = image)
            img.save()

        city_id = request.POST.get('city')
        district_id = request.POST.get('district')
        ward_id = request.POST.get('ward')
        
        post.address = request.POST.get('address_post')
        post.city, post.district, post.ward = getArea(city_id, district_id, ward_id)
        post.save()
        return redirect('settingspage:testPostPage')
    
def testDeleteImagePost(request, postId, imageId):
    try:
        image = Image.objects.get(id = imageId)
        image.isDelete = True
        image.save()
        # JsonResponse()
        return HttpResponseRedirect(reverse('settingspage:testEditPost', args=[postId]))
    except:
        messages.error(request, 'Error')
        # JsonResponse()
        return HttpResponseRedirect(reverse('settingspage:testEditPost', args=[postId]))


def testRecoverDelete(request, postId):
    acc = Account.objects.get(user_ptr=request.user)
    user = Sharer.objects.get(account=acc) if acc.role=='sharer' else Manager.objects.get(account=acc) 
    post = Post.objects.get(id=postId)
    img = post.image_set.all()
    for i in img : 
        i.isDelete = False
        i.save()
    return redirect('settingspage:testPostPage')

def testCreatePosts(request):

    acc = Account.objects.get(user_ptr=request.user)
    user = Sharer.objects.get(account=acc) if acc.role=='sharer' else Manager.objects.get(account=acc)
    if request.method == 'POST':
        post = Post.objects.create(account = acc)
        post.title = request.POST.get('title_post')
        post.content = request.POST.get('content_post')
        if request.POST.get('provider_post') != 'None':
            post.provider_id = request.POST.get('provider_post')
        post.time = timezone.datetime.now()
        images = request.FILES.getlist('images')
        for image in images :
            img = Image.objects.create(post = post, img = image)
            img.save()
        city_id = request.POST.get('city')
        district_id = request.POST.get('district')
        ward_id = request.POST.get('ward')
        
        post.address = request.POST.get('address_post')
        post.city, post.district, post.ward = getArea(city_id, district_id, ward_id)

        post.save()
        return redirect('settingspage:testPostPage')
    else:
        context = {
            'acc': acc,
            'user': user,
            'time' : timezone.datetime.now(),
            'provider': Manager.objects.all()
        }
        return render(request, 'posts/add_post.html', context)

@csrf_exempt
def testDeletePost(request, postId):
    if request.method == 'POST':
        post = Post.objects.get(id=postId)
        post.delete()
        print("đã xóa bài viết")
        return JsonResponse({'success': True})

#Sattistics Page
def statisticsPage(request):
    month = int(request.GET.get('selectedDataMonth', datetime.now().month))
    year = int(request.GET.get('selectedDataYear', datetime.now().year))
    acc = Account.objects.get(user_ptr=request.user)
    user = Sharer.objects.get(account= acc) if acc.role == 'sharer' else Manager.objects.get(account= acc)
    bills = user.bill_set.all()
    monthOfYear = [0]*12
    total = 0
    for bill in bills :
        if bill.status == 'Accept' and bill.time.year == year :
            month1 = bill.time.month
            monthOfYear[month1-1] += bill.price
            total += bill.price
    listRevenue = json.dumps(monthOfYear)

    product_quantity = OrderedDict()
    for product in user.product_set.all():
        product_quantity[product.name] = 0
    user_set = set()
    for bill in bills :
        if bill.status == 'Accept' and bill.time.year == year and bill.time.month == month:
            for order in  bill.order_set.all():
                product = Product.objects.get(id=order.product_id)
                product_quantity[product.name] += order.quantity
            user_set.add(bill.acc)
    age_list = [0]*4
    total_age = 0
    for u in user_set:
        try:
            u = Sharer.objects.get(account=u)
            total_age += 1
            age = u.age
            if age >= 10 and age < 18:
                age_list[0] += 1
            elif age >= 18 and age < 30:
                age_list[1] += 1
            elif age >= 30 and age < 50:
                age_list[2] += 1
            else:
                age_list[3] += 1
        except:
            pass

    if total_age != 0:
        age_phantram = [round(age_list[0]*100/total_age, 2), round(age_list[1]*100/total_age,2), round(age_list[2]*100/total_age, 2), round(age_list[3]*100/total_age, 2)]
    else:
        age_phantram = [0]*4
    sorted_product_quantity = OrderedDict(sorted(product_quantity.items(), key = lambda item: item[1], reverse=True))
    if (len(list(iter(sorted_product_quantity.items()))) >= 1):
        best_seller_name = next(iter(sorted_product_quantity.items()))[0]
        best_seller_quantity = next(iter(sorted_product_quantity.items()))[1]
    else :
        best_seller_name = 'None'
        best_seller_quantity = 'None'
    context = {
        'acc' : acc,
        'monthOfYear' : listRevenue,
        'year' : year,
        'month': month,
        'total' : total,
        'product_quantity' : sorted_product_quantity,
        'product': user.product_set.all(),
        'best_seller_name' : best_seller_name,
        'best_seller_quantity' : best_seller_quantity,
        'age_phantram': json.dumps(age_phantram),
    }
    return render(request, 'statistics/statistics.html', context)








#Post Page
# def postPage(request):
#     acc = Account.objects.get(user_ptr=request.user)
#     user = Sharer.objects.get(account= acc) if acc.role == 'sharer' else Manager.objects.get(account= acc)
#     context = {
#         'acc' : acc,
#         'user' : user,
#     }
#     return render(request, 'post.html', context)

# def deletePost(request, postId):
#     post = Post.objects.get(id = postId)
#     try:
#         post.delete()
#         messages.success(request, 'Xóa bài viết thành công')
#         return redirect('settingspage:postPage')
#     except:
#         messages.error(request, 'Xóa bài viết thất bại')
#         return redirect('settingspage:postPage')

# def changePost(request, postId):
#     if request.method == 'GET':
#         acc = Account.objects.get(user_ptr=request.user)
#         user = Sharer.objects.get(account= acc) if acc.role == 'sharer' else Manager.objects.get(account= acc)
#         post = Post.objects.get(id = postId)
#         img = post.image_set.all()
#         form_post = CreatePostForm(instance=post)
#         form_img = []
#         a = 0
#         for i in img :
#             a = a + 1
#             form_img.append(CreateImgForm(instance=i, prefix=f'form-{a}'))
#         context = {
#             'acc' : acc,
#             'user' : user,
#             'form_post' : form_post,
#             'form_img' : form_img,
#             'post': post,
#             'img' : img,
#         }
#         return render(request, 'add_post.html', context)
#     elif request.method == 'POST':
#         post = Post.objects.get(id = postId)
#         img = post.image_set.all()
#         form_post = CreatePostForm(request.POST, request.FILES, instance=post)
#         form_img = []
#         a = 0
#         for i in img :
#             a = a+1
#             if i.isDelete == True :
#                 i.delete()
#             else :
#                 form_img.append(CreateImgForm(request.POST, request.FILES, prefix=f'form-{a}', instance=i))
#         if form_post.is_valid :
#             for form in form_img :
#                 if not form.is_valid :
#                     messages.error(request, 'Error')
#                     return redirect('settingspage:postPage')

#             newFormPost = form_post.save(commit=False)
#             newFormPost.save()
#             for form in form_img :
#                 newImg = form.save(commit=False)
#                 newImg.save()

#             images = request.FILES.getlist('images')
#             for image in images :
#                 img = Image.objects.create(post = post, img = image)
#                 img.save()

#             return redirect('settingspage:postPage')
#         else :
#             messages.error(request, 'Error')
#             return redirect('settingspage:postPage')



# def addPost(request):
#     acc = Account.objects.get(user_ptr=request.user)
#     user = Sharer.objects.get(account= acc) if acc.role == 'sharer' else Manager.objects.get(account= acc)
#     if request.method == 'POST':
#         post = Post.objects.create(account = acc)
#         form_post = CreatePostForm(request.POST, request.FILES, instance=post)
#         if form_post.is_valid :
#             # try:
#             newPost = form_post.save(commit=False)
#             newPost.save()
#             images = request.FILES.getlist('images')
#             for image in images :
#                 img = Image.objects.create(post = post, img = image)
#                 img.save()

#             messages.success(request, 'Success')
#             return redirect('settingspage:postPage')
#             # except:
#             #     messages.error(request, 'Error')
#             #     return redirect('settingspage:postPage')
#         else :
#             post.delete()
#             messages.error(request, 'Error')
#             return redirect('settingspage:postPage')


#     form_post = CreatePostForm()
#     context = {
#         'form_post': form_post,
#         'acc': acc,
#     }
#     return render(request, 'add_post.html', context)

# def deleteImagePost(request, postId, imageId):
#     try:
#         image = Image.objects.get(id = imageId)
#         image.isDelete = True
#         image.save()
#         return HttpResponseRedirect(reverse('settingspage:changePost', args=[postId]))
#     except:
#         messages.error(request, 'Error')
#         return HttpResponseRedirect(reverse('settingspage:changePost', args=[postId]))

# def unDelete(request, postId, imageId):
#     try:
#         image = Image.objects.get(id = imageId)
#         image.isDelete = False
#         image.save()
#         return HttpResponseRedirect(reverse('settingspage:changePost', args=[postId]))
#     except:
#         return HttpResponseRedirect(reverse('settingspage:changePost', args=[postId]))