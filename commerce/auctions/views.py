from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import get_object_or_404, render  
from .models import User,Category,Listing,Comment,Bid

def addcomment(request,id):
    currentUser=request.user
    listinginfo=Listing.objects.get(pk=id)
    message=request.POST.get('message')
    newComment=Comment(
        author=currentUser,
        listing=listinginfo,
        message=message
    )
    newComment.save()
     
    return HttpResponseRedirect(reverse("listingPage",args=(id,)))



def listingPage(request,id):
    listinginfo=Listing.objects.get(pk=id)
    isListingInWatchlist=request.user in listinginfo.watchlist.all()
    allcomments=Comment.objects.filter(listing=listinginfo)
    owner=request.user.username ==listinginfo.owner.username
    return render (request,"auctions/listing.html",{
        "listing":listinginfo,
        "isListingInWatchlist":isListingInWatchlist,
        "comments": allcomments,
        "owner":owner,
        
    })
def displaywatchlist(request):
    currentUser=request.user
    
    listings = currentUser.watchlist.all() 
    return render(request,"auctions/watchlist.html",{
        "listings": listings 
    })

    

def index(request):
    activeListing=Listing.objects.filter(active=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings":activeListing,
        "category": allCategories,
    })


def removewatchlist(request,id):
   datalisting=Listing.objects.get(pk=id)
   currentUser=request.user
   datalisting.watchlist.remove(currentUser)
   return HttpResponseRedirect(reverse("listingPage",args=(id,)))
   

    
def addwatchlist(request,id):
   data_listing=Listing.objects.get(pk=id)
   currentUser=request.user
   data_listing.watchlist.add(currentUser)
   
   return HttpResponseRedirect(reverse("listingPage",args=(id,)))
   



def categorylist(request):
    if request.method=='POST':
        category_id = request.POST.get('category')
        category=Category.objects.get(id=category_id)
        activeListing=Listing.objects.filter(active=True,category=category)
        allCategories = Category.objects.all()
        return render(request, "auctions/index.html",{
            "listings":activeListing,
            "category": allCategories,
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
    
def create_listing(request):  
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "category": allCategories,
        })
    else:
        title = request.POST['title']
        description = request.POST['description']
        imageurl = request.POST['image']
        price =request.POST.get('price')
        category_id = request.POST['category']
        currentUser = request.user
        categoryData = Category.objects.get(id=category_id)
        bid = Bid(bid=float(price), user=currentUser)  
   
        bid.save()

        newListing = Listing(
            title=title,
            description=description,
            image=imageurl,
            price=bid,
            category=categoryData,
            owner = currentUser
        )
        newListing.save()

        return HttpResponseRedirect(reverse(index))

 
def addBid(request, id):  
    listinginfo = get_object_or_404(Listing, pk=id)   
    isListingInWatchlist = request.user in listinginfo.watchlist.all()  
    isOwner = request.user == listinginfo.owner  

    # Check if the auction is active; if not, return a message  
    if not listinginfo.active:  
        return render(request, "auctions/listing.html", {  
            "listing": listinginfo,  
            "message": "Auction is closed. No bids can be placed.",  
            "update": False,  
            "owner": isOwner,  
            "isListingInWatchlist": isListingInWatchlist,  
        })  

    # Check if a bid was submitted and is valid  
    if 'newBid' in request.POST:  
        newBid = request.POST.get('newBid', None)  
        try:  
            newBidValue = float(newBid)  
            if newBidValue <= 0:  # Ensure the bid is greater than zero  
                raise ValueError("Bid must be greater than zero.")  
        except (ValueError, TypeError):  
            return render(request, "auctions/listing.html", {  
                "listing": listinginfo,  
                "message": "Invalid bid value. Please enter a valid number.",  
                "update": False,  
                "owner": isOwner,  
                "isListingInWatchlist": isListingInWatchlist,  
            })  

        # Get current highest bid value  
        currentBidValue = listinginfo.price.bid if listinginfo.price else 0  

        # Check if the new bid is higher than the current highest bid  
        if newBidValue > currentBidValue:  
            # Create the new bid instance first  
            newBidInstance = Bid(user=request.user, bid=newBidValue)  
            newBidInstance.save()  # Save the bid instance first  
            
            # Associate the bid with the listing  
            newBidInstance.listings.add(listinginfo)  # Now this is safe to call  
            
            # Update the listing price to the new bid  
            listinginfo.price = newBidInstance  # Set the listing price to the new bid instance (if appropriate)  
            listinginfo.save()  

            return render(request, "auctions/listing.html", {  
                "listing": listinginfo,  
                "message": "Successfully updated your bid.",  
                "update": True,  
                "owner": isOwner,  
                "isListingInWatchlist": isListingInWatchlist,  
            })  
        else:  
            return render(request, "auctions/listing.html", {  
                "listing": listinginfo,  
                "message": "Bid must be higher than the current bid.",  
                "update": False,  
                "owner": isOwner,  
                "isListingInWatchlist": isListingInWatchlist,  
            })  
    else:  
        return render(request, "auctions/listing.html", {  
            "listing": listinginfo,  
            "message": "No bid submitted.",  
            "update": False,  
            "owner": isOwner,  
            "isListingInWatchlist": isListingInWatchlist,  
        })


def closeAuction(request, id):  
    listinginfo = get_object_or_404(Listing, pk=id)    
    
    # Check if the auction is already closed  
    if not listinginfo.active:  
        return render(request, "auctions/listing.html", {  
            "listing": listinginfo,  
            "message": "Auction is already closed.",  
            "update": False,  
            "owner": request.user == listinginfo.owner,  
            "isListingInWatchlist": request.user in listinginfo.watchlist.all(),  
        })  

    # Close the auction  
    listinginfo.active = False  
    listinginfo.save()  

    # Fetch all bids and determine the highest bid  
    bids = Bid.objects.all()  # Note: It's better to filter by listing in a proper model.  

    highest_bid = None  
    for bid in bids:  
        if bid.user and bid.user in listinginfo.watchlist.all():  # Adjust this line according to your app logic  
            if highest_bid is None or bid.bid > highest_bid.bid:  
                highest_bid = bid  

    # Determine if the current user is the winner  
    if highest_bid:  
        isWinner = (highest_bid.user == request.user)  # Check if the current user is the highest bidder  
        winning_user = highest_bid.user  # The user with the winning bid  
        winning_bid_amount = highest_bid.bid  # The winning bid amount  
    else:  
        isWinner = False  
        winning_user = None  
        winning_bid_amount = 0  

    isOwner = (request.user == listinginfo.owner)  
    isListingInWatchlist = request.user in listinginfo.watchlist.all()  
    allcomments = Comment.objects.filter(listing=listinginfo)  

    # Render the listing template with the proper context  
    return render(request, "auctions/listing.html", {  
        "listing": listinginfo,  
        "isListingInWatchlist": isListingInWatchlist,  
        "comments": allcomments,  
        "owner": isOwner,  
        "update": True,  
        "message": "Your auction is closed.",  
        "isWinner": isWinner,  
        "winningUser": winning_user,  
        "winningBidAmount": winning_bid_amount,  
    })