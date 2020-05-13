from django.shortcuts import render,get_object_or_404
from .models import Post
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .forms import EmailPostForm
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def post_list(request):
    object_list=Post.published.all()
    paginator=Paginator(object_list,3)
    page=request.GET.get('page')
    try:
        posts=paginator.page(page)

    except PageNotAnInteger:
        posts=paginator.page(1)

    except EmptyPage:
        posts=paginator.page(paginator.num_pages)
   
    return render(request,'blog/post/list.html',{'all_posts':posts})


def post_detail(request,year,month,day,slug):
    post=get_object_or_404(Post,slug=slug,status='published',publish__year=year,publish__month=month,publish__day=day)

    return render(request,'blog/post/detail.html',{'post':post})
    

def post_share(request,post_id):
    post=get_object_or_404(Post,id=post_id,status='published')
    sent=False
    
    if request.method=='POST':
        form=EmailPostForm(request.POST)

        if form.is_valid():
            email_data=form.cleaned_data
            post_url=request.build_absolute_uri(post.get_absolute_url())
            subject='{} ({}) recommends you reading "{}"'.format(email_data['name'],email_data['email'],post.title)
            # Christine (gacuirichristine@gmail.com) recommends reading "Uhuru visists Kisumu"
            message='Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title,post_url,email_data['name'],email_data['comments'])
            send_mail(subject,message,settings.EMAIL_HOST_USER,[email_data['to']])
            sent=True
            

    else:
        form=EmailPostForm()
    
    return render(request,'blog/post/share.html',{'post':post,'form':form,'sent':sent})