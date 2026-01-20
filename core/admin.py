from django.contrib import admin
from .models import User, Truck, Driver, Client, Booking, Expense, FuelLog

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'origin', 'destination', 'driver', 'total_amount_received', 'total_expenses_display', 'profit_or_loss_display', 'status')

    def total_expenses_display(self, obj):
        return f"Rs. {obj.total_expenses():,.2f}"

    def profit_or_loss_display(self, obj):
        amount = obj.profit_or_loss()
        return f"{'Profit' if amount >= 0 else 'Loss'}: Rs. {abs(amount):,.2f}"

    total_expenses_display.short_description = "Total Expenses"
    profit_or_loss_display.short_description = "Profit / Loss"

@admin.register(FuelLog)
class FuelLogAdmin(admin.ModelAdmin):
    list_display = ('truck', 'date', 'liters', 'rate_per_liter', 'total_cost', 'odometer_reading', 'last_odometer_reading', 'fuel_efficiency')
    list_filter = ('truck', 'date')
    search_fields = ('truck__number_plate', 'location')
# Register other models
admin.site.register(User)
admin.site.register(Truck)
admin.site.register(Driver)
admin.site.register(Client)
admin.site.register(Expense)

