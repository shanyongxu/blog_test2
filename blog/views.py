#coding:utf-8
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse
from blog.models import *
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from comments.forms import *
from django.db.models import *
from django.views.generic.list import ListView
import markdown

from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
import pygments

class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 3
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        pagination_data = self.pagination_data(paginator, page, is_paginated)

        context.update(pagination_data)
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}
                # 当前页左边连续的页码号，初始值为空
        left = []

        # 当前页右边连续的页码号，初始值为空
        right = []

        # 标示第一页页码后是否需要显示省略号
        left_has_more = False

        # 标示最后一页页码前是否需要显示省略号
        right_has_more = False

        # 标示是否需要显示第一页的页码号。
        # 因为如果当前页左边的连续页码号中已经含有第一页的页码号，此时就无需再显示第一页的页码号
        # 其它情况下第一页的页码是始终需要显示的。
        first = False

        # 标示是否需要显示最后一页的页码号。
        # 需要此指示变量的理由和上面相同。
        last = False

        # 获得用户当前请求的页码号
        page_number = page.number

        # 获得分页后的总页数
        total_pages = paginator.num_pages

        # 获得整个分页页码列表，比如分了四页，那么就是 [1, 2, 3, 4]
        page_range = paginator.page_range

        if page_number == 1:
            # 如果用户请求的是第一页的数据，那么当前页左边的不需要数据，因此 left=[]（已默认为空）
            # 获取当前页右边的连续页码号。
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 right = [2, 3]
            # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            right = page_range[page_number:page_number + 2]

            # 如果最右边的页码号比最后一页的页码号减去 1 还要小，
            # 说明最右边的页码号和最后一页的页码号之间还有其它页码，因此需要显示省略号，通过 right_has_more 来指示
            if right[-1] < total_pages - 1:
                right_has_more = True

            # 如果最右边的页码号比最后一页的页码号小，说明当前页右边的连续页码号中不包含最后一页的页码
            # 所以需要显示最后一页的页码号，通过 last 来指示
            if right[-1] < total_pages:
                last = True

        elif page_number == total_pages:
            # 如果用户请求的是最后一页的数据，那么当前页右边就不需要数据，因此 right=[]（已默认为空）
            # 获取当前页左边的连续页码号。
            # 比如分页页码列表是 [1, 2, 3, 4]，那么获取的就是 left = [2, 3]
            # 这里只获取了当前页码后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

            # 如果最左边的页码号比第 2 页页码号还大，
            # 说明最左边的页码号和第一页的页码号之间还有其它页码，因此需要显示省略号，通过 left_has_more 来指示
            if left[0] > 2:
                left_has_more = True

            # 如果最左边的页码号比第一页的页码号大，说明当前页左边的连续页码号中不包含第一页的页码
            # 所以需要显示第一页的页码号，通过 first 来指示
            if left[0] > 1:
                first = True
        else:
            # 用户请求的既不是最后一页，也不是第一页，则需要获取当前页左右两边的连续页码号
            # 这里只获取了当前页码前后连续两个页码，你可以更改这个数字以获取更多页码。
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 2]

            # 是否需要显示最后一页和最后一页前的省略号
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            # 是否需要显示第一页和第一页后的省略号
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        context = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }

        return context

def search(request):
    q = request.GET.get('q')
    error_msg = ''

    if not q:
        error_msg = '请输入关键词'        
        return render(request, 'blog/index.html', {'error_msg': error_msg})
    post_list = Post.objects.filter(title__icontains=q)
    #post_list = Post.objects.all()
    return render(request, 'blog/index.html', {'error_msg':error_msg, 'post_list': post_list})

def index(request):
    post_list = Post.objects.all().order_by('-created_time')
    paginator = Paginator(post_list, 3)
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'blog/index.html', context={'post_list': post_list})

def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    #md = markdown.Markdown(extensions=[
    #                                 'markdown.extensions.extra',
    #                                 'markdown.extensions.codehilite',
    #                                 'markdown.extensions.toc',
    #                              ])
    #form = CommentForm()
    #comment_list = post.comment_set.all()
    #context = {
    #    'post': post,
    #    'form': form,
    #    'comment_list': comment_list
    #}
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        TocExtension(slugify=slugify),
    ])
    post.body = md.convert(post.body)
    form = CommentForm()
    comment_list = post.comment_set.all()
    context = {
        'post': post,
        'toc': md.toc,
        'form': form,
        'comment_list': comment_list        
    }

    return render(request, 'blog/detail.html', context=context)


def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year=year, created_time__month=month)
    return render(request, 'blog/index.html', context={'post_list': post_list})


def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})

