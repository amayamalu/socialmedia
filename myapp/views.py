from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.views.generic import CreateView,TemplateView,FormView,UpdateView,ListView,DetailView
from django.views.generic import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout
from django.db.models import Q

from myapp.forms import SignUpForm,SignInForm,ProfileEditForm,PostForm,CoverpicForm,ProfilepicForm
from myapp.models import UserProfile,Posts,Comments



class SignUpView(CreateView):
    model=User
    form_class=SignUpForm
    template_name="register.html"
    success_url=reverse_lazy("signin")

    def form_valid(self,form):
        messages.success(self.request,"account has been created!!")
        return super().form_valid(form)
    
    def form_invalid(self,form):
        messages.error(self.request,"failed to create account")
        return super().form_invalid(form)
    

class SignInView(FormView):
    form_class=SignInForm
    template_name="login.html"

    # def get(self,request,*args,**kwargs):
    #     form=self.form_class
    #     return render(request,self.template_name,{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=self.form_class(request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            usr=authenticate(request,username=uname,password=pwd)
            if usr:
                login(request,usr)
                messages.success(request,"login succesfully")
                return redirect("index")
            messages.error(request,"invalid credentail")
            return render(request,self.template_name,{"form":form})


class IndexView(CreateView,ListView):
    model=Posts
    template_name="index.html"
    form_class=PostForm
    context_object_name="posts"
    success_url=reverse_lazy("index")


    def form_valid(self,form):
        form.instance.user=self.request.user
        return super().form_valid(form)


class ProfileEditView(UpdateView):
    model=UserProfile
    form_class=ProfileEditForm
    template_name="profile-edit.html"
    success_url=reverse_lazy("index")

    def form_valid(self, form):
        messages.success(self.request,"updated")
        return super().form_valid(form)
    

def add_like_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    post_obj=Posts.objects.get(id=id)
    post_obj.liked_by.add(request.user)
    return redirect("index")


def add_comment_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    post_obj=Posts.objects.get(id=id)
    comment=request.POST.get("comment")
    Comments.objects.create(user=request.user,post=post_obj,comment_text=comment)
    return redirect("index")

def sign_out_view(request,*args,**kwargs):
    logout(request)
    return redirect("signin")


def comment_remove_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    cmnt_obj=Comments.objects.get(id=id)

    if request.user==cmnt_obj.user:
        cmnt_obj.delete()
        return redirect("index")
    else:
        messages.error(request,"please contact the admin")
        return redirect("signin")
    

class ProfileDetailView(DetailView):
    model=UserProfile
    template_name="profile.html"
    context_object_name="profile"

def change_coverpic_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    prof_obj=UserProfile.objects.get(id=id)
    form=CoverpicForm(instance=prof_obj,data=request.POST,files=request.FILES)
    if form.is_valid():
        form.save()
        return redirect("profile-detail",pk=id)

    return redirect("profile-detail",pk=id)

def change_profilepic_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    profile_obj=UserProfile.objects.get(id=id)
    form=ProfilepicForm(instance=profile_obj,data=request.POST,files=request.FILES)
    if form.is_valid():
        form.save()
        return redirect("profile-detail",pk=id)
    return redirect("profile-detail",pk=id)


class ProfileListView(ListView):
    model=UserProfile
    template_name="profile-list.html"
    context_object_name="profiles"
    
    #change queryset
    def get_queryset(self):
        return UserProfile.objects.exclude(user=self.request.user)
    

    def post(self,request,*args,**kwargs):
        pname=request.POST.get("username")
        qs=UserProfile.objects.filter(Q(user__username__icontains=pname) | Q(user__first_name__icontains=pname))
        messages.error(request,"No  records has been found")
        return render(request,self.template_name,{"profiles":qs})
    

def follow_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    prof_obj=UserProfile.objects.get(id=id)
    user_prof=request.user.profile
    user_prof.following.add(prof_obj)
    user_prof.save()
    return redirect("index")
    

def unfollow_view(request,*args,**kwargs):
    id=kwargs.get("pk")
    prof_obj=UserProfile.objects.get(id=id)
    user_prof=request.user.profile
    user_prof.following.remove(prof_obj)
    user_prof.save()
    return redirect("index")