from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# All models for the auction site 

class User(AbstractUser):
    pass

class Category(models.Model):
    """ List of available categories
    """
    name = models.CharField(max_length=20)
    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
     """ manage all user Listings
     """
     title = models.CharField(max_length=30)
     description = models.TextField()
     starting_bid = models.IntegerField()
     current_bid = models.IntegerField(default=0)
     image = models.ImageField(upload_to='uploads/', blank=True, null=True)
     listing_date = models.DateField()
     bid_closed = models.BooleanField(default=False)  # bid open by default
     highest_bidder = models.ForeignKey(
             User,
             on_delete=models.CASCADE,
             null=True,
             related_name="bids_won"
             ) # potential bid winner
     listed_by = models.ForeignKey(
             User,
             on_delete=models.CASCADE,
             related_name="listings"  # Provide a related_name
             )
     category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)

     def save(self, *args, **kwargs):
         if self.current_bid == 0:
             self.current_bid = self.starting_bid
         if self.category_id is None:
             default_category = Category.objects.get(name='Others')  # Get the "Others" category
             self.category = default_category
         super().save(*args, **kwargs)
     
     def __str__(self):
         return f"{self.title} by {self.listed_by.username}"

class Bid(models.Model):
    """ Bids made on auctions
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE) # user who bid
    bid = models.IntegerField()
    bid_time = models.DateField()
    listing = models.ForeignKey(Listing, 
                                related_name="bids",
                                on_delete=models.CASCADE) # many-to-one rlship w/ item
    def __str__(self):
        return f"Bid by {self.user.username}: {self.bid}"

class Comment(models.Model):
    """ comments on auctions posted
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments") # commentor
    text = models.CharField(max_length=100)
    comment_date = models.DateField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE) # rlship with listed item

    class Meta:
        ordering = ['-comment_date'] # order according to date
    def __str__(self):
        return f"Comment by {self.user.username} on {self.comment_date}"

class Watchlist(models.Model):
    """ user's watchlist
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ManyToManyField(Listing)

    def __str__(self):
        return f"{self.user}'s watchlist"
