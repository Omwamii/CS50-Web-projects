from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import datetime
from .models import User, Listing, Bid, Comment, Watchlist, Category
from .forms import ListingForm, BidForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages


def custom_404(request, exception):
    """ render custom 404 page
    """
    return render(request, 'auctions/404.html', status=404)

def index(request):
    listings = Listing.objects.filter(bid_closed=False).all()
    if request.user.is_authenticated:
        try:
            # newly registered user might not have watchlist obj created
            watchlist = Watchlist.objects.get(user=request.user)
        except ObjectDoesNotExist:
            watchlist = None
        if watchlist is None:
            watchlist = Watchlist.objects.create(user=request.user)

        num_watchlist = len(watchlist.item.all())
    else:
        num_watchlist = 0 # user not signed in (won't be shown)
    return render(request, "auctions/index.html",
                  {"listings": listings, "count": num_watchlist})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, 'Invalid username and/or password.')
            return render(request, "auctions/login.html")
    else:
        return render(request, "auctions/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.warning(request, 'Passwords must match')
            return render(request, "auctions/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, 'Username already taken.')
            return render(request, "auctions/register.html")
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def show_categories(request):
    """ direct user to categories page
    """
    categories = Category.objects.all().order_by('name')
    num_watchlist = len(Watchlist.objects.get(user=request.user).item.all())
    return render(request, "auctions/categories.html",
                  {"categories": categories, "count": num_watchlist})

@login_required
def show_watchlist(request):
    """ direct user to watchlist page
    """
    watch_list = Watchlist.objects.get(user=request.user)
    watch_list = watch_list.item.all()
    num_watchlist = len(watch_list)
    return render(request,"auctions/watchlist.html",
                  {"watchlist": watch_list, "count": num_watchlist})

@login_required
def create_listing(request):
    """ allow user to create a listing item
    """
    num_watchlist = len(Watchlist.objects.get(user=request.user).item.all())
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            desc = form.cleaned_data['description']
            bid = form.cleaned_data['starting_bid']
            image = form.cleaned_data['image']
            category = form.cleaned_data['category']
            date = datetime.utcnow()
            listed_by = request.user 

            listing = Listing.objects.create(title=title, description=desc, 
                                             starting_bid=bid, 
                                             image=image, 
                                             category=category,
                                             listing_date=date,
                                             listed_by=listed_by)
            if listing is not None:
                listing.save()
                print('Listing create')
                messages.success(request, 'Listing created successfully')
            else:
                print("Error creating listing")
        else:
            print(form.errors)
            messages.error(request, 'Unable to create Listing! invalid form')
        return redirect('create')
    else:
        form = ListingForm()
        return render(request, "auctions/createList.html",
                      {"count": num_watchlist,
                       "form": form})


@login_required
def goto_listing(request, listing_id):
    """ take user to spefic listing
    """
    num_watchlist = len(Watchlist.objects.get(user=request.user).item.all())
    item = Listing.objects.get(id=listing_id) # listing item
    if item.listed_by == request.user:
        is_lister = True
    else:
        is_lister = False
    num_bids = len(Bid.objects.filter(listing=item).all())
    bid_info = f"{num_bids}bid(s) so far."
    if request.method == "GET":
        try:
            watchlist = Watchlist.objects.get(user=request.user)
        except ObjectDoesNotExist :
            watchlist = None
        if watchlist is None:
            val = "Add to watchlist"
        else:
            if item in watchlist.item.all():
                val = "Remove from watchlist"
            else:
                val = "Add to watchlist"
        if item.highest_bidder == request.user:
            bid_info += " Your bid is the current bid"
        else:
            if item.highest_bidder is None: # no bid yet
                pass
            else:
                bid_info += f" User {item.highest_bidder.id}'s bid is the current bid"
        try:
            user_bid = Bid.objects.filter(user=request.user).all()
        except ObjectDoesNotExist:
            placed_a_bid = False # user never placed a bid on item
        else:
            if len(user_bid) == 0:
                placed_a_bid = False
            else:
                placed_a_bid = True
            
        if item.bid_closed:
            # get the time a winning bid was placed (close to time it closed)
            highest_bid_placed = Bid.objects.get(bid=item.current_bid)
            bid_close_time = highest_bid_placed.bid_time
        else:
            bid_close_time = None
        comments = Comment.objects.filter(listing=item).all()
        return render(request, "auctions/listing.html", {"item": item,
                                                         "count": num_watchlist,
                                                         "bid_info": bid_info,
                                                         "bid_close_time": bid_close_time,
                                                         "placed_bid": placed_a_bid,
                                                         "val": val,
                                                         "is_lister": is_lister,
                                                         "comments": comments})

    if request.method == "POST":
        if request.POST.get('close_bid') is not None:
            if item.current_bid == item.starting_bid: # no bid placed
                messages.error(request, 'Cannot close auction, no bid placed')
            else:
                # lister is closing auction on item
                item.bid_closed = True
                item.save()
                # delete all other bids -> irrelevant + save space
                highest_bid_obj = item.bids.get(bid=item.current_bid) # get winning bid
                if highest_bid_obj:
                    print("The highest bid -> ", end="")
                    print(highest_bid_obj)
                # delete all other bids
                item.bids.exclude(id=highest_bid_obj.id).delete()

        # user has commented / posted a bid
        if request.POST.get('bid') is not None:
            # check if current bid price is higher than placed bid
            if int(request.POST['bid']) > int(item.current_bid):
                # only place bid higher than starting
                bid_price = int(request.POST['bid'])
                user = request.user
                date = datetime.utcnow()
                listing = Listing.objects.get(id=listing_id)
                bid = Bid.objects.create(user=user, bid=bid_price,
                                         bid_time=date,
                                         listing=listing)
                if bid is not None:
                    bid.save()
                    item.current_bid = bid_price
                    item.highest_bidder = request.user
                    item.save()
                    messages.success(request, 'Bid placed successfully')
            else:
                # return error could not place bid
                message = f"Bid is too low. Current bid is at {item.current_bid}"
                messages.error(request, message)

        if request.POST.get('comment') is not None:
            # create comment attached to listing
            user = request.user
            text = request.POST['comment']
            date = datetime.utcnow()
            listing = Listing.objects.get(id=listing_id)

            comment = Comment.objects.create(user=user, text=text,
                                             comment_date=date,
                                             listing=listing)
            if comment is not None:
                comment.save()
                messages.success(request, 'Comment posted successfully')
            else:
                # return error -> comment could not be saved
                messages.error(request, 'Unable to comment')

        if request.POST.get('watch_item') is not None:
            # add item to watchlist if not already
            watch_item_id = request.POST.get('watch_item')

            if watch_item_id:
                item = Listing.objects.get(id=watch_item_id)
                try:
                    watchlist = Watchlist.objects.get(user=request.user)
                except ObjectDoesNotExist:
                    watchlist = None

                if watchlist is None:
                    watchlist = Watchlist.objects.create(user=request.user)

                if item in watchlist.item.all():
                    watchlist.item.remove(item)  # Remove item from watchlist
                else:
                    watchlist.item.add(item)  # Add item to watchlist 
        return redirect('listing', listing_id=listing_id)  # Redirect back to the listing page

@login_required
def goto_category(request, name):
    # fetch all objects with the category <name> and render
    num_watchlist = len(Watchlist.objects.get(user=request.user).item.all())
    category_obj = Category.objects.get(name=name)
    category_items = Listing.objects.filter(category=category_obj).all()
    return render(request, "auctions/category.html",
                  {"count": num_watchlist,
                   "items": category_items,
                   "category_name": name})
