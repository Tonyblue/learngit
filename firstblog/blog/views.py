from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post, Category, Tag
import markdown
from comments.forms import CommentForm
from django.views.generic import ListView, DetailView
from django.db.models import Q

class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 2
#def index(request):
    #post_list = Post.objects.all()
    #return render(request, 'blog/index.html', context = {'post_list': post_list})

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_views()
        return response

    def get_object(self, queryset=None):
        post = super(PostDetailView, self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            #TocExtension(slugify=slugify),
        ])
        post.body = md.convert(post.body)
        post.toc = md.toc
        return post

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comments_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context

""""
def detail(request, pk):
    post = get_object_or_404(Post, pk = pk)
    post.increase_views()
    post.body = markdown.markdown(post.body,
                                  extensions = [
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',
                                  ])
    form = CommentForm()
    comment_list = post.comments_set.all()
    context = {
        'post': post,
        'form': form,
        'comment_list': comment_list
    }
    return render(request, 'blog/detail.html', context = context)
"""
def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year = year,
                                    created_time__month = month)
    return render(request, 'blog/index.html', context = {'post_list':post_list})

class CategoryView(IndexView):
    def get_queryset(self):
        cate = get_object_or_404(Category, pk = self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category = cate)

#def category(request, pk):
    #cate = get_object_or_404(Category, pk = pk)
    #post_list = Post.objects.filter(category = cate)
    #return render(request, 'blog/index.html', context = {'post_list': post_list})

class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk = self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags = tag)

def search(request):
    q = request.GET.get('q')
    error_msg = ''

    if not q:
        error_msg = "请输入关键词"
        return render(request, 'blog/index.html', {'error_msg': error_msg})
    post_list = Post.objects.filter(Q(title__icontains = q)| Q(body__icontains = q))
    return render(request, 'blog/index.html', {'error_msg': error_msg, 'post_list': post_list})