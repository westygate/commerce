from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django  import forms
from .models import User, Listing, Bid, Comment, Category
from datetime import date
from django.contrib.auth.decorators import login_required

class CreateListing(forms.Form):
    title=forms.CharField(label="Title",widget=forms.TextInput(attrs={'placeholder': 'Title of listing'}))
    description= forms.CharField(label="Description",widget=forms.Textarea(
        attrs={ "placeholder": "Enter description here", "rows":6}))
    bid=forms.IntegerField(label="Price",widget=forms.NumberInput(attrs={'placeholder': 'Start price'}))
    image=forms.CharField(label="Image",widget=forms.TextInput(attrs={'placeholder': 'URL to image'}))

class BidForm(forms.Form):
    bid=forms.IntegerField(label=False,widget=forms.NumberInput(attrs={'placeholder': 'Bid'}))

class CommentForm(forms.Form):
    comment=forms.CharField(label=False,widget=forms.Textarea(attrs={'placeholder': 'Your comment', "rows":6, "cols":100}))


def index(request):
    listings=Listing.objects.all().filter(isClosed=False)
    return render(request, "auctions/index.html",{
        "title": "Active Listing", "listings":listings
        })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
    
@login_required(login_url="/login")   
def create(request):
    categories=Category.objects.all
    if request.method == "POST":
        form=CreateListing(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            bid = form.cleaned_data["bid"]
            image = form.cleaned_data["image"]
            category = request.POST["category"]
            category_obj = Category.objects.get(id=category)
            try:
                listing = Listing(name=title, description=description,
                                  price=bid, category=category_obj, image=image,
                                  owner=request.user)
                listing.save()
                return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
            except IntegrityError:
                return render(request, "auctions/create.html",{
        "form": form, "categories": categories
            })
        else:
            return render(request, "auctions/create.html",{
        "form": form, "categories": categories
            })
    return render(request, "auctions/create.html",{
        "form": CreateListing(), "categories": categories
        })

def categories(request):
    categories=Category.objects.all
    return render(request, "auctions/categories.html",{
        "categories": categories
        })

def one_category(request, title):
    category_obj = Category.objects.get(name=title)
    listings=Listing.objects.filter(category=category_obj, isClosed=False)
    return render(request, "auctions/index.html",{
        "title": "Active Listing", "title2": title,"listings":listings
        })

def listing(request, id):
    listing=Listing.objects.get(id=id)
    user=request.user
    watchlist = False
    users = listing.watchlist.all() 
    if user in users:
        watchlist=True
    closeBtn=False
    if listing.owner == user and listing.isClosed==False:
        closeBtn=True
    
    comments=Comment.objects.filter(listing=listing)
    new_comment= CommentForm(prefix="comment")   
    if listing.winner==user:
        return render(request, "auctions/listing.html",{
        "listing": listing, "watchlist": watchlist,
        "message": "You are winner", "comments": comments, "new_comment": new_comment
        })
    
    new_bid=BidForm( prefix="bid")
    
    if request.method == "POST":
        if "bid" in request.POST:
            form=BidForm(request.POST, prefix="bid")
            if form.is_valid():
                if listing.bid != None:
                    cur_bid=listing.bid.bid
                else:
                    cur_bid=0
                bid = form.cleaned_data["bid"]
                if bid > cur_bid and bid>=listing.price:
                    try:
                        new_bid=Bid(bid=bid, owner=request.user)
                        new_bid.save()
                        listing.price = bid
                        listing.bid=new_bid
                        listing.save()
                        message="Your bid was added successfully"
                        success=True
                    except IntegrityError:
                        message="Some errors"
                    
                else:
                     message="Your bid is too small"
                     success=False
                return render(request, "auctions/listing.html",{
                    "listing": listing, "watchlist": watchlist, "bid": form,
                    "message": message,"success":success, "closeBtn": closeBtn, "comments": comments, "new_comment": new_comment
                })
            else:
                return render(request, "auctions/listing.html",{
                "listing": listing, "watchlist": watchlist, "bid": form,
                "closeBtn": closeBtn, "comments": comments, "new_comment": new_comment
                })
        elif "comment" in request.POST:
            form=CommentForm(request.POST, prefix="comment")
            if form.is_valid():
                comment=form.cleaned_data["comment"]
                create=date.today().strftime('%Y-%m-%d')
                try:
                    new_comment=Comment(comment=comment, owner=user,listing=listing)
                    new_comment.save()
                    return HttpResponseRedirect(reverse('listing', args=(listing.id,)))
                except IntegrityError:
                    return render(request, "auctions/listing.html",{
                    "listing": listing, "watchlist": watchlist, "new_comment": form,
                    "message": "message", "closeBtn": closeBtn, "comments": comments, "bid": new_bid
                })
            else:
                return render(request, "auctions/listing.html",{
                    "listing": listing, "watchlist": watchlist, "new_comment": form,
                    "message": "message", "closeBtn": closeBtn, "comments": comments, "bid": new_bid
                })
      
    return render(request, "auctions/listing.html",{
        "listing": listing, "watchlist": watchlist,
        "bid": new_bid, "closeBtn": closeBtn, "comments": comments,
        "new_comment": new_comment
        })



@login_required(login_url="/login") 
def watchlist(request, id, action):
    user=request.user
    listing=Listing.objects.get(id=id)
    if action == 'add':
        listing.watchlist.add(user)
    if action == 'remove':
        listing.watchlist.remove(user)
    return HttpResponseRedirect(reverse('listing', args=(id,)))

@login_required(login_url="/login") 
def show_watchlist(request):
    user=request.user
    listings = user.listings.all()
    return render(request, "auctions/index.html",{
        "title": "Watchlist", "listings":listings
        })

def close(request, id):
    listing=Listing.objects.get(id=id)
    if listing.bid != None:
        winner=listing.bid.owner
    else:
        winner=None
    listing.winner=winner
    listing.isClosed=True
    listing.name = listing.name + ' (Closed)'
    listing.save()
    return HttpResponseRedirect(reverse('listing', args=(id,)))