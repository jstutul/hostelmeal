from django.db import models
from django.contrib.auth.models import User
import datetime


class MealSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    noon = models.BooleanField(default=False)
    night = models.BooleanField(default=False)

    guest_noon = models.PositiveIntegerField(default=0)
    guest_night = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class Bazar(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.amount}"


class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"





class ExtraChargeNew(models.Model):
    CHARGE_TYPE_CHOICES = [
        ('current', 'Extra Current Bill'),
        ('mowla', 'Extra Mowla Bill'),
        ('others', 'Others'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    charge_type = models.CharField(max_length=20, choices=CHARGE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'date', 'charge_type')  # update unique_together

    def __str__(self):
        return f"{self.user.username} - {self.get_charge_type_display()} - {self.date}"
