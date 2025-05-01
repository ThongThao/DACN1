from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'

class Staff(models.Model):
    MORNING = 'morning'
    AFTERNOON = 'afternoon'
    EVENING = 'evening'
    FULL_DAY = 'full_day'
    
    SHIFT_CHOICES = [
        (MORNING, 'Sáng (7h-12h)'),
        (AFTERNOON, 'Chiều (12h-17h)'),
        (EVENING, 'Tối (17h-22h)'),
        (FULL_DAY, 'Cả ngày (7h-22h)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    date = models.DateField(null=True, blank=True, verbose_name='Ngày làm việc')  # From StaffSchedule
    schedule_status = models.BooleanField(default=True, verbose_name='Trạng thái lịch')  # True: active, False: cancelled
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.full_name} - {self.get_shift_display()}"
    
    class Meta:
        verbose_name = 'Nhân viên'
        verbose_name_plural = 'Nhân viên'

from django.db import models
from django.core.validators import MinValueValidator

class VehicleType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Tên loại xe')
    first_hour_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Giá đầu tiên (1h)')
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Giá tiếp theo (/30 phút)')
    overnight_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Giá qua đêm')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Loại xe'
        verbose_name_plural = 'Loại xe'

class ParkingArea(models.Model):
    ACTIVE = 'active'
    MAINTENANCE = 'maintenance'
    CLOSED = 'closed'
    
    STATUS_CHOICES = [
        (ACTIVE, 'Đang hoạt động'),
        (MAINTENANCE, 'Đang bảo trì'),
        (CLOSED, 'Đã đóng'),
    ]
    
    name = models.CharField(max_length=100)
    max_capacity = models.PositiveIntegerField()
    current_occupancy = models.PositiveIntegerField(default=0)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    class Meta:
        verbose_name = 'Khu vực đỗ xe'
        verbose_name_plural = 'Khu vực đỗ xe'

class Vehicle(models.Model):
    license_plate = models.CharField(max_length=20, unique=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.PROTECT)
    image = models.ImageField(upload_to='license_plates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.license_plate} ({self.vehicle_type.name()})"
    
    class Meta:
        verbose_name = 'Phương tiện'
        verbose_name_plural = 'Phương tiện'

class ParkingRecord(models.Model):
    PENDING = 'pending'
    PAID = 'paid'
    CANCELLED = 'cancelled'
    
    PAYMENT_STATUS_CHOICES = [
        (PENDING, 'Chưa thanh toán'),
        (PAID, 'Đã thanh toán'),
        (CANCELLED, 'Đã hủy'),
    ]
    
    CASH = 'cash'
    BANKING = 'banking'
    MOMO = 'momo'
    ZALO_PAY = 'zalo_pay'
    
    PAYMENT_METHOD_CHOICES = [
        (CASH, 'Tiền mặt'),
        (BANKING, 'Chuyển khoản'),
        (MOMO, 'Ví MoMo'),
        (ZALO_PAY, 'ZaloPay'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    parking_area = models.ForeignKey(ParkingArea, on_delete=models.PROTECT)
    staff = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PENDING)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_time = models.DateTimeField(blank=True, null=True)
    payment_success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__():
        return f"{self.vehicle.license_plate} - {self.check_in_time}"
    
    class Meta:
        verbose_name = 'Bản ghi đỗ xe'
        verbose_name_plural = 'Bản ghi đỗ xe'