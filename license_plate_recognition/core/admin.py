from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin thêm', {'fields': ('phone', 'address')}),
    )

class StaffAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'shift', 'date', 'schedule_status', 'user')
    search_fields = ('full_name', 'phone', 'user__username')
    list_filter = ('shift', 'schedule_status')

class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'first_hour_price', 'additional_price', 'overnight_price')
    search_fields = ('name',)

class ParkingAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'vehicle_type', 'max_capacity', 'current_occupancy', 'status')
    list_filter = ('vehicle_type', 'status')
    search_fields = ('name',)

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'vehicle_type', 'image')
    search_fields = ('license_plate',)
    list_filter = ('vehicle_type',)

class ParkingRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'parking_area', 'staff', 'check_in_time', 'check_out_time', 'payment_status', 'payment_method')
    list_filter = ('payment_status', 'parking_area', 'vehicle__vehicle_type', 'payment_method', 'staff')
    search_fields = ('vehicle__license_plate', 'transaction_id', 'staff__full_name')
    date_hierarchy = 'check_in_time'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(VehicleType, VehicleTypeAdmin)
admin.site.register(ParkingArea, ParkingAreaAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(ParkingRecord, ParkingRecordAdmin)