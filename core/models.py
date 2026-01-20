from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('accountant', 'Accountant'),
        ('driver', 'Driver'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='manager')

    def __str__(self):
        return self.username
    
class Truck(models.Model):
    number_plate = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=50)
    capacity_tons = models.FloatField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.number_plate


class Driver(models.Model):
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    assigned_truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, null=True)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    goods_description = models.TextField()
    weight_kg = models.FloatField()
    departure_date = models.DateField()
    arrival_date = models.DateField(null=True, blank=True)
    total_amount_received = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def total_expenses(self):
        return sum(exp.amount for exp in self.expenses.all())

    def profit_or_loss(self):
        return self.total_amount_received - self.total_expenses()

    def __str__(self):
        return f"Trip {self.id} - {self.origin} to {self.destination}"


class Expense(models.Model):
    EXPENSE_TYPES = [
    ('toll', 'Toll Tax'),
    ('fuel', 'Fuel'),
    ('food', 'Food'),
    ('police', 'Police/Bribe'),
    ('driver', 'Driver'),
    ('helper', 'Helper'),
    ('loading', 'Loading'),
    ('unloading', 'Unloading'),
    ('commission', 'Commission'),          # Naya
    ('garage', 'Garage/Maintenance'),     # Naya (ghari ka kaam, mistri)
    ('mechanic', 'Mechanic'),         # Naya
    ('motorway_tax', 'Motorway Tax'),     # Naya
    ('security', 'Security'),         # Naya
    ('kaanta', 'Kaanta'),         # Naya
    ('other', 'Other'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='expenses')
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.expense_type} - Rs. {self.amount}"


class FuelLog(models.Model):
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    liters = models.FloatField()
    rate_per_liter = models.DecimalField(max_digits=6, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    odometer_reading = models.PositiveIntegerField(help_text="Truck's meter reading at time of fueling")
    last_odometer_reading = models.PositiveIntegerField(null=True, blank=True, help_text="Previous reading (auto-filled)")

    date = models.DateField()
    
    def fuel_efficiency(self):
        """Returns KM per Liter if last reading is available"""
        if self.last_odometer_reading:
            distance = self.odometer_reading - self.last_odometer_reading
            return round(distance / self.liters, 2) if self.liters > 0 else None
        return None

    def save(self, *args, **kwargs):
        self.total_cost = self.liters * float(self.rate_per_liter)
        
        if not self.last_odometer_reading:
            previous_log = FuelLog.objects.filter(
                truck=self.truck,
                date=self.date,
                pk__lt=self.pk if self.pk else 9999999  # exclude current record
            ).order_by('-pk').first()

            if not previous_log:
                # If same-day previous not found, check earlier dates
                previous_log = FuelLog.objects.filter(
                    truck=self.truck,
                    date__lt=self.date
                ).order_by('-date', '-pk').first()

            if previous_log:
                self.last_odometer_reading = previous_log.odometer_reading

        super().save(*args, **kwargs)


    def __str__(self):
        return f"Fuel - {self.truck.number_plate} - Rs. {self.total_cost}"
