from django.shortcuts import render,get_object_or_404
from .models import Post,Comment
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .forms import EmailPostForm,CommentForm
from django.core.mail import send_mail
from django.conf import settings
from taggit.models import Tag

# Create your views here.
def post_list(request,tag_slug=None):
    object_list=Post.published.all()
    paginator=Paginator(object_list,3)
    page=request.GET.get('page')
    tag=None

    if tag_slug:
        tag=get_object_or_404(Tag,slug=tag_slug)
        object_list=object_list.filter(tags__in=[tag])

     

    try:
        posts=paginator.page(page)

    except PageNotAnInteger:
        posts=paginator.page(1)

    except EmptyPage:
        posts=paginator.page(paginator.num_pages)
   
    return render(request,'blog/post/list.html',{'all_posts':posts,'tag':tag})


def post_detail(request,year,month,day,slug):
    post=get_object_or_404(Post,slug=slug,status='published',publish__year=year,publish__month=month,publish__day=day)

    #  List of active comments for this post
    comments=post.comments.filter(active=True)

    new_comment=None

    if request.method=='POST' :
        comment_form=CommentForm(data=request.POST)

        if comment_form.is_valid():
            # Create Comment object but don't save to database yet 
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post=post
            # Save the comment to the database
            new_comment.save()

    else:
        comment_form=CommentForm()
            

    return render(request,'blog/post/detail.html',{'post':post,'comments':comments,'new_comment':new_comment,'comment_form':comment_form})
    

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