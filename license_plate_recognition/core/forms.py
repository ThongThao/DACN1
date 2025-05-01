from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
import re
from .models import User, Staff

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Tên đăng nhập",
        widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True})
    )
    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    error_messages = {
        'invalid_login': "Tên đăng nhập hoặc mật khẩu không đúng. Vui lòng thử lại.",
        'inactive': "Tài khoản của bạn đã bị vô hiệu hóa.",
    }

class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Họ và tên'
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Số điện thoại'
    )
    username = forms.CharField(
        label="Tên đăng nhập",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Xác nhận mật khẩu",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'phone', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Tên đăng nhập chỉ được chứa chữ cái, số và dấu gạch dưới (_).")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Tên đăng nhập đã tồn tại.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email đã được sử dụng.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^\+?\d{10,11}$', phone):
            raise ValidationError("Số điện thoại không hợp lệ. Vui lòng nhập từ 10 hoặc 11 chữ số.")
        return phone

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if password1 and len(password1) < 8:
            raise ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Mật khẩu và xác nhận mật khẩu không khớp.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.phone = self.cleaned_data['phone']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserEditForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Họ và tên'
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Số điện thoại'
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    is_staff = forms.BooleanField(
        label="Quyền quản trị",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ['full_name', 'phone', 'email', 'is_staff']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            raise ValidationError("Email đã được sử dụng.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^\+?\d{10,11}$', phone):
            raise ValidationError("Số điện thoại không hợp lệ. Vui lòng nhập từ 10 hoặc 11 chữ số.")
        return phone

class StaffEditForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Họ và tên'
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Số điện thoại'
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        label='Địa chỉ'
    )
    shift = forms.ChoiceField(
        choices=Staff.SHIFT_CHOICES,
        required=False,
        label='Ca làm việc',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        required=False,
        label='Ngày làm việc',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    schedule_status = forms.BooleanField(
        required=False,
        initial=True,
        label='Trạng thái lịch (Hoạt động)',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Staff
        fields = ['full_name', 'phone', 'address', 'shift', 'date', 'schedule_status']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^\+?\d{10,11}$', phone):
            raise ValidationE
        
from django import forms
from .models import VehicleType

class VehicleTypeForm(forms.ModelForm):
    class Meta:
        model = VehicleType
        fields = ['name', 'first_hour_price', 'additional_price', 'overnight_price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên loại xe'}),
            'first_hour_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'additional_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'overnight_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'name': 'Tên loại xe',
            'first_hour_price': 'Giá đầu tiên (1h)',
            'additional_price': 'Giá tiếp theo (/30 phút)',
            'overnight_price': 'Giá qua đêm',
        }

    def clean(self):
        cleaned_data = super().clean()
        first_hour_price = cleaned_data.get('first_hour_price')
        additional_price = cleaned_data.get('additional_price')
        overnight_price = cleaned_data.get('overnight_price')

        if first_hour_price is not None and first_hour_price < 0:
            raise forms.ValidationError("Giá đầu tiên không được âm.")
        if additional_price is not None and additional_price < 0:
            raise forms.ValidationError("Giá tiếp theo không được âm.")
        if overnight_price is not None and overnight_price < 0:
            raise forms.ValidationError("Giá qua đêm không được âm.")

        return cleaned_data

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Tên loại xe không được để trống.")
        if VehicleType.objects.filter(name=name).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Tên loại xe này đã tồn tại.")
        return name
    
from django import forms
from .models import ParkingArea

class ParkingAreaForm(forms.ModelForm):
    class Meta:
        model = ParkingArea
        fields = ['name', 'max_capacity', 'vehicle_type', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên khu vực'}),
            'max_capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Tên khu vực',
            'max_capacity': 'Sức chứa tối đa',
            'vehicle_type': 'Loại xe',
            'status': 'Trạng thái',
        }

    def clean(self):
        cleaned_data = super().clean()
        max_capacity = cleaned_data.get('max_capacity')
        if max_capacity is not None and max_capacity < 1:
            raise forms.ValidationError("Sức chứa tối đa phải lớn hơn 0.")
        return cleaned_data

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Tên khu vực không được để trống.")
        if ParkingArea.objects.filter(name=name).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Tên khu vực này đã tồn tại.")
        return name

    def clean_max_capacity(self):
        max_capacity = self.cleaned_data.get('max_capacity')
        if self.instance and self.instance.current_occupancy > max_capacity:
            raise forms.ValidationError("Sức chứa tối đa không được nhỏ hơn số xe hiện tại.")
        return max_capacity