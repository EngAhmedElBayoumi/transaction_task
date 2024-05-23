from django.db import models
from django.utils.text import slugify
#import time zone
from django.utils import timezone


class Account(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(unique=True, max_length=150)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            queryset = Account.objects.filter(slug=self.slug).exclude(id=self.id)
            counter = 1
            while queryset.exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                queryset = Account.objects.filter(slug=self.slug).exclude(id=self.id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    
class Transaction(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='receiver')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()    
    def __str__(self):
        return f'{self.sender} sent {self.amount} to {self.receiver}'
    class Meta:
        ordering = ['-date']
    def save(self, *args, **kwargs):
        if not self.date:
            self.date = timezone.now()
        
        super().save(*args, **kwargs)
    
    
