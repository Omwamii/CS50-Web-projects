from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import User
from .models import Post
import json

def get_user(request):
    ''' API to return user's username (check if anonymous)'''
    u_obj = request.user
    try:
        print(f"API: get_user {u_obj.profile_pic}")
    except AttributeError:
        profile_pic = request.build_absolute_uri(settings.STATIC_URL + 'network/images/default.png')
    else:
        if u_obj.profile_pic:
            profile_pic = request.build_absolute_uri(u_obj.profile_pic.url)
        else:
            # set a default profile photo
            profile_pic = request.build_absolute_uri(settings.STATIC_URL + 'network/images/default.png')

    user_data = {'id': u_obj.id, 'username': u_obj.username, 'profile_pic': profile_pic,
                 'is_authenticated': u_obj.is_authenticated}
    u_data = json.dumps(user_data)
    return JsonResponse(u_data, safe=False)

def get_user_stats(request, user_id):
    ''' API to return complete user obj for rendering '''
    u_obj = User.objects.get(id=user_id)
    r_user = request.user
    if u_obj:
        user_posts = list()
        for post in Post.objects.filter(poster=u_obj).all():
            post_likes = post.liked_by.all()
            user_liked = True if r_user in post_likes else False
            post_data = {'id': post.id, 'text': post.text, 'time': str(post.time),
                        'like_count': post.liked_by.count(),
                        'posted_by': post.posted_by, 'user_liked': user_liked}
            user_posts.append(post_data)
        liked_posts = list()

        for liked_p in u_obj.likes.all():
            post_likes = liked_p.liked_by.all()
            if liked_p.poster.profile_pic:
                user_image = request.build_absolute_uri(liked_p.poster.profile_pic.url)
            else:
                user_image = request.build_absolute_uri(settings.STATIC_URL + 'network/images/default.png')
            user_liked = True if r_user in post_likes else False
            post_data = {'id': liked_p.id, 'text': liked_p.text, 'time': str(liked_p.time),
                        'like_count': liked_p.liked_by.count(),
                        'poster_id': liked_p.poster.id, 'posted_by': liked_p.posted_by,
                        'user_liked': user_liked, 'profile_pic': user_image}
            liked_posts.append(post_data)

        following = u_obj.following.count()
        followers = 0
        is_following = False  # check if requesting user is following profile user
        for u_user in User.objects.all():
            u_following = u_user.following.all()
            if u_obj in u_following:
                followers += 1
                if r_user == u_user:
                    is_following = True  # req user follows profile user
        try:
            print(f"API: get_user_stats {u_obj.profile_pic}")
        except AttributeError:
            # Anonymous user
            profile_pic_url = request.build_absolute_uri(settings.STATIC_URL + 'network/images/default.png')
        else:
            if u_obj.profile_pic:
                profile_pic_url = request.build_absolute_uri(u_obj.profile_pic.url)
            else:
                # set a default profile photo
                profile_pic_url = request.build_absolute_uri(settings.STATIC_URL + 'network/images/default.png')

        is_me = False
        if r_user == u_obj:
            # visited own profile
            is_me = True
        user = {'username': u_obj.username,
                'all_names': u_obj.first_name + u_obj.last_name,
                'following': following,
                'followers': followers,
                'posts': user_posts,
                'liked_posts': liked_posts,
                'picture': profile_pic_url,
                'user_id': u_obj.id,
                'is_following': is_following,
                'is_me': is_me,
            }
    else:
        user = None
    user_data = json.dumps(user)
    return JsonResponse(user_data, safe=False)

def get_poster(request, post_id):
    ''' API to get poster_id from post id'''
    post = Post.objects.get(pk=post_id)
    poster = post.poster.id  # return id of the poster
    return JsonResponse(poster, safe=False)

def index(request):
    return render(request, "network/index.html")

@csrf_exempt
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        data = json.loads(request.body)
        username = data["username"]
        password = data["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Logged in successfully'})
             # return HttpResponseRedirect(reverse("index"))
        else:
            return JsonResponse({
                "message": "Invalid username and/or password."
            })
    else:
        return JsonResponse({'message': "Invalid request method: GET"})

def logout_view(request):
    logout(request)
    return JsonResponse({"message": "You are logged out"})
    # return HttpResponseRedirect(reverse("index"))


@csrf_exempt
def register(request):
    if request.method == "POST":
        data = request.POST  # from react api
        username = data["username"]
        email = data["email"]
        pic = request.FILES.get('pic')


        # Ensure password matches confirmation
        password = data["password"]
        confirmation = data["confirmation"]
        if password != confirmation:
            return JsonResponse({
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.profile_pic = pic
            user.save()
        except IntegrityError:
            return JsonResponse({
                "message": "Username already taken."
            })
        login(request, user)
        return JsonResponse({'message': 'Registration successful'})
    else:
        # will be handled by react
        return JsonResponse({'message': 'Invalid request method: GET'})

@csrf_exempt
def create_post(request):
    ''' Save posts created by users and return the post created'''
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    new_post = Post(poster=request.user, text=data)
    new_post.save()
    u_obj = User.objects.get(pk=new_post.poster.id)
    if u_obj.profile_pic:
        user_image = request.build_absolute_uri(u_obj.profile_pic.url)
    else:
        # set a default profile photo
        user_image = request.build_absolute_uri(settings.STATIC_URL + 'network/images/default.png')
    likes = new_post.liked_by.all()
    user_liked = True if request.user in likes else False
    post_data = {'id': new_post.id, 'text': new_post.text, 'time': str(new_post.time),
                'like_count': new_post.liked_by.count(),
                'poster_id': new_post.poster.id, 'poster_username': new_post.posted_by,
                'profile_pic': user_image,
                'edited': new_post.edited, 'user_liked': user_liked}
    u_post = json.dumps(post_data)
    return JsonResponse(u_post, safe=False)

@csrf_exempt
def edit_post(request, post_id):
    ''' Edit a post and return edited post'''
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    old_post = Post.objects.get(pk=post_id)
    old_post.text = data
    old_post.edited = True
    old_post.save()
    u_obj = User.objects.get(pk=old_post.poster.id)
    if u_obj.profile_pic:
        user_image = request.build_absolute_uri(u_obj.profile_pic.url)
    else:
        # set a default profile photo
        user_image = request.build_absolute_uri(settings.STATIC_URL + 'network/images/default.png')
    likes = old_post.liked_by.all()
    user_liked = True if request.user in likes else False
    post_data = {'id': old_post.id, 'text': old_post.text, 'time': str(old_post.time),
                'like_count': old_post.liked_by.count(),
                'poster_id': old_post.poster.id, 'poster_username': old_post.posted_by,
                'profile_pic': user_image,
                'edited': old_post.edited, 'user_liked': user_liked}
    u_post = json.dumps(post_data)
    return JsonResponse(u_post, safe=False)

def load_posts(request, type_of_posts):
    ''' Load posts created by users
        type_of_posts: All posts | Following posts
    '''
    if type_of_posts == 'all':
        print('''\n-------------------------- Loading all posts -------------------------\n''')
        posts = Post.objects.all().order_by('-time')  # load posts in reverse chronology
    elif type_of_posts == 'following':
        print('''\n------------------------- loading following posts ---------------------\n''')
        following = request.user.following.all()
        posts = Post.objects.filter(poster__in=following).order_by('-time')

    # Paginate the posts
    p = Paginator(posts, 10) # load 10 posts per page
    page_num = request.GET.get('page')
    posts_page = p.get_page(page_num)
    # pagination data
    page_data = {
            'next': posts_page.next_page_number() if posts_page.has_next() else None,
            'previous': posts_page.previous_page_number() if posts_page.has_previous() else None,
            'current': posts_page.number,
            'total': p.num_pages,
        }
    # Serialize the paginated posts to JSON

    posts_to_render = list()
    for post in posts_page:
        u_obj = User.objects.get(pk=post.poster.id)
        likes = post.liked_by.all()
        user_liked = True if request.user in likes else False
        if u_obj.profile_pic:
            user_image = request.build_absolute_uri(u_obj.profile_pic.url) 
        else:
            user_image = request.build_absolute_uri(settings.STATIC_URL + 'network/images/default.png')
        post_data = {'id': post.id, 'text': post.text, 'time': str(post.time), 'like_count': post.liked_by.count(),
                     'poster_id': post.poster.id, 'poster_username': post.posted_by, 'profile_pic': user_image,
                     'edited': post.edited, 'user_liked': user_liked}
        posts_to_render.append(post_data)
    response = {'posts': posts_to_render, 'pagination': page_data}
    response = json.dumps(response)
    return JsonResponse(response, safe=False)


def like_post(request, postId):
    ''' API endpoint to like a post'''
    post = Post.objects.get(pk=postId)
    if not post:
        return JsonResponse({'Error': 'No such post'})
     # Check if the user has already liked the post
    users_who_liked = post.liked_by.all()
    if request.user in users_who_liked:
        # If the user has already liked, remove the like
        post.liked_by.remove(request.user)
    else:
        # If the user hasn't liked, add the like
        post.liked_by.add(request.user)
    post.save()
    u_obj = User.objects.get(pk=post.poster.id)
    if u_obj.profile_pic:
        user_image = request.build_absolute_uri(u_obj.profile_pic.url)
    else:
        # set a default profile photo
        user_image = request.build_absolute_uri(settings.STATIC_URL + 'network/images/default.png')
    likes = post.liked_by.all()
    user_liked = True if request.user in likes else False
    post_data = {'id': post.id, 'text': post.text, 'time': str(post.time),
                'like_count': post.liked_by.count(),
                'poster_id': post.poster.id, 'poster_username': post.posted_by,
                'profile_pic': user_image,
                'edited': post.edited, 'user_liked': user_liked}
    u_post = json.dumps(post_data)
    return JsonResponse(u_post, safe=False)

def follow(request, user_id):
    ''' API to follow a user
        user_id: id of user to follow
    '''
    request_user = request.user
    user_to_follow = User.objects.get(pk=user_id)
    if user_to_follow:
        following = request_user.following.all()
        if user_to_follow in following:
            request_user.following.remove(user_to_follow)
            user_followed = False
        else:
            request_user.following.add(user_to_follow)
            user_followed = True
        request_user.save()
    return JsonResponse(user_followed, safe=False)