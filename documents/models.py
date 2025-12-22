from django.db import models
from buyer.models import User

class PriceList(models.Model):
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, db_column='uploaded_by') 
    filename = models.CharField(max_length=255)
    file_url = models.CharField(max_length=500)  # store document URL
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'price_lists'
        managed  = False

    def __str__(self):
        return f"{self.filename} - uploaded by {self.uploaded_by.fullname}"
