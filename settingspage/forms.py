from django import forms
from homepage.models import *

class UpdateSharerForm(forms.ModelForm):
    class Meta:
        model = Sharer
        fields = ("name", "avatar")

class UpdateManagerForm(forms.ModelForm):
    class Meta:
        model = Manager
        fields = ("name","avatar", "address", "bio")

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'address', 'provider')

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('type', 'name','describe' , 'price', 'img',)

class CreateImgForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('img',)
        # widgets = {
        #     'img' : forms.FileInput(attrs={'class' : '11'})
        # }
        
class CreatePostFormTest(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'address', 
                  'city', 'district', 'ward',
                  'provider')
