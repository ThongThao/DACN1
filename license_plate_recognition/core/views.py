from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .models import User, Staff
from .forms import RegistrationForm, CustomLoginForm, UserEditForm, StaffEditForm
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from .models import Vehicle
from django.utils import timezone
from .forms import VehicleTypeForm
from .models import VehicleType, ParkingArea
from .forms import ParkingAreaForm  
from .recognizer import detect_license_plate
from django.http import JsonResponse
from django.db.models import F
import random
import string
import os
import logging
from django.core.files.storage import default_storage
from django.conf import settings
from decimal import Decimal
from core.models import Vehicle, ParkingRecord, VehicleType, ParkingArea
from core.recognizer import detect_license_plate_checkout  
User = get_user_model()

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('login')

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def staff_management(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                Staff.objects.create(
                    user=user,
                    full_name=form.cleaned_data.get('full_name') or user.username,
                    phone=form.cleaned_data.get('phone', ''),
                    address='',  # Default empty
                    shift='full_day',  # Default
                    date=None,  # Default null
                    schedule_status=True  # Default
                )
                messages.success(request, 'Thêm nhân viên thành công!')
            else:
                messages.error(request, 'Lỗi khi thêm nhân viên. Vui lòng kiểm tra lại.')
        
        elif action == 'edit':
            user_id = request.POST.get('user_id')
            user = User.objects.get(id=user_id)
            staff = Staff.objects.get(user=user)
            user_form = UserEditForm(request.POST, instance=user)
            staff_form = StaffEditForm(request.POST, instance=staff)
            if user_form.is_valid() and staff_form.is_valid():
                user_form.save()
                staff_form.save()
                messages.success(request, 'Cập nhật nhân viên thành công!')
            else:
                messages.error(request, 'Lỗi khi cập nhật nhân viên. Vui lòng kiểm tra lại.')
        
        elif action == 'delete':
            user_id = request.POST.get('user_id')
            user = User.objects.get(id=user_id)
            if user != request.user:
                user.delete()  # Deletes User and Staff via CASCADE
                messages.success(request, 'Xóa nhân viên thành công!')
            else:
                messages.error(request, 'Không thể xóa tài khoản của chính bạn!')
        
        return redirect('staff_management')

    staff_list = Staff.objects.select_related('user').all()  # Query Staff table
    paginator = Paginator(staff_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    create_form = RegistrationForm()
    edit_form = UserEditForm()
    staff_edit_form = StaffEditForm()
    
    return render(request, 'staff_management.html', {
        'staff_list': page_obj,
        'page_obj': page_obj,
        'create_form': create_form,
        'edit_form': edit_form,
        'staff_edit_form': staff_edit_form
    })


@login_required
def area_management(request):
    return render(request, 'area_management.html')
@login_required
def price_management(request):
    return render(request, 'price_management.html')

@login_required
def check_in(request):
    return render(request, 'check_in.html')



@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công!')
    return redirect('login')

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Staff.objects.create(
                user=user,
                full_name=form.cleaned_data.get('full_name') or user.username,
                phone=form.cleaned_data.get('phone', ''),
                address='',  # Default empty
                shift='full_day',  # Default
                date=None,  # Default null
                schedule_status=True  # Default
            )
            login(request, user)
            messages.success(request, 'Đăng ký thành công!')
            return redirect('home')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                if hasattr(user, 'staff'):
                    messages.success(request, f'Xin chào nhân viên {user.staff.full_name}!')
                else:
                    messages.success(request, f'Xin chào {user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def account_management(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                Staff.objects.create(
                    user=user,
                    full_name=form.cleaned_data.get('full_name') or user.username,
                    phone=form.cleaned_data.get('phone', ''),
                    address='',  # Default empty
                    shift='full_day',  # Default
                    date=None,  # Default null
                    schedule_status=True  # Default
                )
                messages.success(request, 'Tạo tài khoản thành công!')
            else:
                messages.error(request, 'Lỗi khi tạo tài khoản. Vui lòng kiểm tra lại.')

        elif action == 'edit':
            user_id = request.POST.get('user_id')
            user = User.objects.get(id=user_id)
            form = UserEditForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Cập nhật tài khoản thành công!')
            else:
                messages.error(request, 'Lỗi khi cập nhật tài khoản. Vui lòng kiểm tra lại.')

        elif action == 'delete':
            user_id = request.POST.get('user_id')
            user = User.objects.get(id=user_id)
            if user != request.user:
                user.delete()
                messages.success(request, 'Xóa tài khoản thành công!')
            else:
                messages.error(request, 'Không thể xóa tài khoản của chính bạn!')

        return redirect('account_management')

    users = User.objects.all()
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    create_form = RegistrationForm()
    edit_form = UserEditForm()
    
    return render(request, 'account_management.html', {
        'users': page_obj,
        'page_obj': page_obj,
        'create_form': create_form,
        'edit_form': edit_form
    })



@login_required

def price_management(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            form = VehicleTypeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thêm loại xe thành công!')
            else:
                messages.error(request, 'Lỗi khi thêm loại xe. Vui lòng kiểm tra lại.')
                return render(request, 'price_management.html', {
                    'vehicle_types': VehicleType.objects.all(),
                    'create_form': form,
                    'edit_form': VehicleTypeForm()
                })

        elif action == 'edit':
            vehicle_type_id = request.POST.get('vehicle_type_id')
            try:
                vehicle_type = VehicleType.objects.get(id=vehicle_type_id)
                form = VehicleTypeForm(request.POST, instance=vehicle_type)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Cập nhật giá xe thành công!')
                else:
                    messages.error(request, 'Lỗi khi cập nhật giá xe. Vui lòng kiểm tra lại.')
                    return render(request, 'price_management.html', {
                        'vehicle_types': VehicleType.objects.all(),
                        'create_form': VehicleTypeForm(),
                        'edit_form': form
                    })
            except VehicleType.DoesNotExist:
                messages.error(request, 'Loại xe không tồn tại.')

        elif action == 'delete':
            vehicle_type_id = request.POST.get('vehicle_type_id')
            try:
                vehicle_type = VehicleType.objects.get(id=vehicle_type_id)
                if ParkingArea.objects.filter(vehicle_type=vehicle_type).exists():
                    messages.error(request, 'Không thể xóa loại xe vì nó đang được sử dụng trong khu vực đỗ xe.')
                else:
                    vehicle_type.delete()
                    messages.success(request, 'Xóa loại xe thành công!')
            except VehicleType.DoesNotExist:
                messages.error(request, 'Loại xe không tồn tại.')

        return redirect('price_management')

    vehicle_types = VehicleType.objects.all()
    print(vehicle_types)  # Thêm dòng này để kiểm tra

    create_form = VehicleTypeForm()
    edit_form = VehicleTypeForm()


    return render(request, 'price_management.html', {
        'vehicle_types': vehicle_types,
        'create_form': create_form,
        'edit_form': edit_form
    })



def area_management(request):
    vehicle_types = VehicleType.objects.all()
    parking_areas = ParkingArea.objects.all()
    create_form = ParkingAreaForm()
    edit_form = ParkingAreaForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            create_form = ParkingAreaForm(request.POST)
            if create_form.is_valid():
                create_form.save()
                return redirect('area_management')
        elif action == 'edit':
            area_id = request.POST.get('area_id')
            area = ParkingArea.objects.get(id=area_id)
            edit_form = ParkingAreaForm(request.POST, instance=area)
            if edit_form.is_valid():
                edit_form.save()
                return redirect('area_management')
        elif action == 'delete':
            area_id = request.POST.get('area_id')
            ParkingArea.objects.get(id=area_id).delete()
            return redirect('area_management')

    return render(request, 'area_management.html', {
        'vehicle_types': vehicle_types,
        'parking_areas': parking_areas,
        'create_form': create_form,
        'edit_form': edit_form,
    })

@login_required


def recognize_license_plate(request):
    if request.method == 'POST' and request.FILES.get('frame'):
        frame = request.FILES['frame']
        if not frame.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            return JsonResponse({'error': 'Chỉ hỗ trợ file ảnh JPG hoặc PNG'}, status=400)
        if frame.size > 5 * 1024 * 1024:  # 5MB limit
            return JsonResponse({'error': 'File quá lớn'}, status=400)

        file_path = default_storage.save('temp/webcam_frame.jpg', frame)
        full_path = os.path.join(default_storage.location, file_path)

        try:
            license_plate, cloudinary_url = detect_license_plate(full_path)
            if license_plate:
                return JsonResponse({
                    'license_plate': license_plate,
                    'crop_image_path': cloudinary_url  # Return Cloudinary URL
                })
            return JsonResponse({'error': 'No license plate detected'}, status=200)
        finally:
            default_storage.delete(file_path)
    return JsonResponse({'error': 'Invalid request'}, status=400)



logger = logging.getLogger(__name__)

def get_available_parking_areas(request):
    vehicle_type_id = request.GET.get('vehicle_type_id')
    logger.debug(f"Received vehicle_type_id: {vehicle_type_id}")
    if not vehicle_type_id:
        return JsonResponse({'error': 'Yêu cầu ID loại phương tiện'}, status=400)

    try:
        vehicle_type_id = int(vehicle_type_id)
        logger.debug(f"Querying ParkingArea with vehicle_type_id={vehicle_type_id}, status='active'")
        parking_areas = ParkingArea.objects.filter(
            vehicle_type__id=vehicle_type_id,
            status='active',
            current_occupancy__lt=F('max_capacity')
        ).values('id', 'name')
        logger.debug(f"Query result: {list(parking_areas)}")

        if not parking_areas:
            return JsonResponse({'error': 'Không tìm thấy khu vực đỗ xe phù hợp'}, status=200)

        return JsonResponse({'parking_areas': list(parking_areas)})
    except ValueError:
        logger.error(f"Invalid vehicle_type_id: {vehicle_type_id}")
        return JsonResponse({'error': 'ID loại phương tiện không hợp lệ'}, status=400)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def generate_unique_ticket_code():
    """Generate a random 4-character ticket code (alphanumeric) unique among pending records."""
    characters = string.ascii_uppercase + string.digits  # A-Z, 0-9
    max_attempts = 10
    
    for _ in range(max_attempts):
        code = ''.join(random.choices(characters, k=4))
        if not ParkingRecord.objects.filter(ticket_code=code, payment_status='pending').exists():
            return code
    raise ValueError("Unable to generate unique ticket code after multiple attempts")

# Updated vehicle_check_in view
logger = logging.getLogger(__name__)

@login_required
def vehicle_check_in(request):
    if request.method == 'POST':
        license_plate = request.POST.get('license_plate').strip().upper()
        vehicle_type_id = request.POST.get('vehicle_type')
        area_id = request.POST.get('parking_area')
        cloudinary_url = request.POST.get('crop_image_path')  # Now contains Cloudinary URL

        logger.info(f"Received check-in: license_plate={license_plate}, cloudinary_url={cloudinary_url}")

        if not (license_plate and vehicle_type_id and area_id):
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin.')
            logger.error("Missing required fields")
            return redirect('vehicle_check_in')

        # Validate staff
        staff = request.user

        # Fetch vehicle type and parking area
        try:
            vehicle_type = VehicleType.objects.get(id=vehicle_type_id)
            parking_area = ParkingArea.objects.get(id=area_id)
        except (VehicleType.DoesNotExist, ParkingArea.DoesNotExist):
            messages.error(request, 'Loại xe hoặc khu vực không hợp lệ.')
            logger.error("Invalid vehicle type or parking area")
            return redirect('vehicle_check_in')

        # Check parking area capacity
        if parking_area.current_occupancy >= parking_area.max_capacity:
            messages.error(request, 'Khu vực này đã đầy.')
            logger.error(f"Parking area {parking_area.name} is full")
            return redirect('vehicle_check_in')

        # Prevent duplicate active records
        if ParkingRecord.objects.filter(vehicle__license_plate=license_plate, check_out_time__isnull=True).exists():
            messages.error(request, 'Xe này đã được nhận và chưa trả.')
            logger.error(f"Vehicle {license_plate} already checked in")
            return redirect('vehicle_check_in')

        # Create or update vehicle
        try:
            vehicle, created = Vehicle.objects.get_or_create(
                license_plate=license_plate,
                defaults={'vehicle_type': vehicle_type, 'image': cloudinary_url}
            )
            if not created:
                vehicle.vehicle_type = vehicle_type
                if cloudinary_url:
                    vehicle.image = cloudinary_url  # Store Cloudinary URL
                vehicle.save()
            logger.info(f"Saved vehicle: license_plate={vehicle.license_plate}, image={vehicle.image}")
        except Exception as e:
            logger.error(f"Error saving vehicle: {e}")
            messages.error(request, 'Lỗi khi lưu thông tin xe.')
            return redirect('vehicle_check_in')

        # Update parking area occupancy
        try:
            parking_area.current_occupancy += 1
            parking_area.save()
            logger.info(f"Updated parking area: {parking_area.name}, occupancy={parking_area.current_occupancy}")
        except Exception as e:
            logger.error(f"Error updating parking area: {e}")
            messages.error(request, 'Lỗi khi cập nhật khu vực đỗ xe.')
            return redirect('vehicle_check_in')

        # Generate unique ticket code
        try:
            ticket_code = generate_unique_ticket_code()
        except ValueError as e:
            logger.error(f"Error generating ticket code: {e}")
            messages.error(request, 'Lỗi khi tạo mã vé xe.')
            return redirect('vehicle_check_in')

        # Create parking record with ticket code
        try:
            ParkingRecord.objects.create(
                vehicle=vehicle,
                parking_area=parking_area,
                staff=staff,
                check_in_time=timezone.now(),
                ticket_code=ticket_code  # Assign ticket code
            )
            logger.info(f"Created parking record for vehicle: {vehicle.license_plate}, ticket_code={ticket_code}")
        except Exception as e:
            logger.error(f"Error creating parking record: {e}")
            messages.error(request, 'Lỗi khi tạo bản ghi đỗ xe.')
            return redirect('vehicle_check_in')

        messages.success(request, f"Đã nhận xe biển số {license_plate} với mã vé {ticket_code}")
        return redirect('vehicle_check_in')

    # GET request
    vehicle_types = VehicleType.objects.all()
    recent_records = ParkingRecord.objects.select_related('vehicle', 'parking_area', 'staff') \
                                       .filter(payment_status='pending').order_by('-check_in_time')[:5]

    return render(request, 'check_in.html', {
        'vehicle_types': vehicle_types,
        'recent_records': recent_records,
    })


logger = logging.getLogger(__name__)

@login_required
def checkout_view(request):
    """
    View xử lý giao diện và logic checkout xe ra.
    """
    if request.method == 'POST':
        # Xử lý nhận diện biển số qua AJAX
        if 'image' in request.FILES:
            image = request.FILES['image']
            # Lưu ảnh tạm thời
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, f"temp_{timezone.now().timestamp()}.jpg")
            with open(temp_path, 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            
            try:
                # Nhận diện biển số
                license_plate = detect_license_plate_checkout(temp_path)
                if not license_plate:
                    return JsonResponse({'error': 'Không nhận diện được biển số'}, status=400)
                
                # Tìm bản ghi đỗ xe
                try:
                    parking_record = ParkingRecord.objects.get(
                        vehicle__license_plate=license_plate,
                        payment_status=ParkingRecord.PENDING
                    )
                except ParkingRecord.DoesNotExist:
                    return JsonResponse({'error': f'Không tìm thấy bản ghi đỗ xe cho biển số {license_plate}'}, status=404)

                # Tính toán chi phí
                check_out_time = timezone.now()
                duration = check_out_time - parking_record.check_in_time

                hours = duration.total_seconds() / 3600
                
                vehicle_type = parking_record.vehicle.vehicle_type
                if hours <= 5:
                    total_amount = vehicle_type.first_hour_price
                else:
                    extra_hours = hours - 5
                    total_amount = vehicle_type.first_hour_price + Decimal(extra_hours) * vehicle_type.additional_price * 2

                # Kiểm tra qua đêm
                if parking_record.check_in_time.date() != check_out_time.date():
                    total_amount += vehicle_type.overnight_price

                # Trả về thông tin
                return JsonResponse({
                    'license_plate': license_plate,
                    'check_in_time': parking_record.check_in_time.strftime('%H:%M %d/%m/%Y'),
                    'check_out_time': check_out_time.strftime('%H:%M %d/%m/%Y'),
                    'duration': str(duration),
                    'vehicle_type': vehicle_type.name,
                    'total_amount': f"{total_amount:,.0f} VND"
                })

            finally:
                # Xóa ảnh tạm
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        # Xử lý xác nhận thanh toán
        elif 'license_plate' in request.POST:
            license_plate = request.POST['license_plate']
            payment_method = request.POST.get('payment_method', ParkingRecord.CASH)
            
            try:
                parking_record = ParkingRecord.objects.get(
                    vehicle__license_plate=license_plate,
                    payment_status=ParkingRecord.PENDING
                )
            except ParkingRecord.DoesNotExist:
                return JsonResponse({'error': f'Không tìm thấy bản ghi đỗ xe cho biển số {license_plate}'}, status=404)

            # Cập nhật bản ghi
            check_out_time = timezone.now()
            duration = check_out_time - parking_record.check_in_time
            hours = duration.total_seconds() / 3600
            vehicle_type = parking_record.vehicle.vehicle_type
            
            if hours <= 5:
                total_amount = vehicle_type.first_hour_price
            else:
                extra_hours = hours - 5
                total_amount = vehicle_type.first_hour_price + Decimal(extra_hours) * vehicle_type.additional_price * 2
            
            if parking_record.check_in_time.date() != check_out_time.date():
                total_amount += vehicle_type.overnight_price

            parking_record.check_out_time = check_out_time
            parking_record.total_amount = total_amount
            parking_record.payment_status = ParkingRecord.PAID
            parking_record.payment_method = payment_method
            parking_record.payment_time = check_out_time
            parking_record.payment_success = True
            parking_record.staff = request.user
            parking_record.save()

            # Cập nhật số lượng xe trong khu vực
            parking_area = parking_record.parking_area
            parking_area.current_occupancy = max(0, parking_area.current_occupancy - 1)
            parking_area.save()

            return JsonResponse({'success': 'Thanh toán thành công'})

    # Lấy danh sách loại xe và giá
    vehicle_types = VehicleType.objects.all()
    return render(request, 'check_out.html', {'vehicle_types': vehicle_types})

def calculate_parking_fee(check_in_time, check_out_time, vehicle_type):
    """
    Tính phí đỗ xe mới: 5 giờ đầu theo giá cố định, sau đó mỗi giờ thêm tính gấp đôi giá 30 phút.
    """
    duration = check_out_time - check_in_time
    hours = duration.total_seconds() / 3600
    
    if hours <= 5:
        total_amount = vehicle_type.first_hour_price
    else:
        extra_hours = hours - 5
        total_amount = vehicle_type.first_hour_price + Decimal(extra_hours) * vehicle_type.additional_price * 2

    if check_in_time.date() != check_out_time.date():
        total_amount += vehicle_type.overnight_price

    return total_amount

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import ParkingRecord, Vehicle, VehicleType, Staff, ParkingArea
import datetime

@login_required
def home_view(request):
    today = timezone.now().date()
    
    # --- Tổng quan hệ thống ---
    # Số xe trong bãi (payment_status=PENDING)
    vehicles_in_parking = ParkingRecord.objects.filter(
        payment_status='PENDING'
    ).count()
    
    # Doanh thu tháng này
    revenue_month = ParkingRecord.objects.filter(
        payment_time__month=today.month,
        payment_time__year=today.year,
        payment_status='PAID'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Số chỗ trống hiện tại
    total_capacity = ParkingArea.objects.aggregate(total=Sum('max_capacity'))['total'] or 0
    total_occupied = ParkingArea.objects.aggregate(total=Sum('current_occupancy'))['total'] or 0
    total_free_slots = max(0, total_capacity - total_occupied)
    
    # Tỷ lệ sử dụng bãi đỗ (%)
    usage_percentage = (total_occupied / total_capacity * 100) if total_capacity > 0 else 0
    
    # Hoạt động gần đây (3 bản ghi gần nhất)
    recent_activities = ParkingRecord.objects.select_related('vehicle__vehicle_type').order_by('-check_in_time')[:3]
    
    # --- Biểu đồ cột: Số xe vào/ra theo ngày (7 ngày gần đây) ---
    vehicles_in_out_by_day = []
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        vehicles_in = ParkingRecord.objects.filter(
            check_in_time__date=date
        ).count()
        vehicles_out = ParkingRecord.objects.filter(
            check_out_time__date=date,
            payment_status__in=['PAID', 'PENDING']

        ).count()
        vehicles_in_out_by_day.append({
            'date': date.strftime('%a'),
            'vehicles_in': vehicles_in,
            'vehicles_out': vehicles_out
        })
    
    # --- Biểu đồ tròn: Phân bố loại xe đã ra vào bãi ---
    vehicle_type_distribution = ParkingRecord.objects.filter(
       payment_status__in=['PAID', 'PENDING']

    ).values('vehicle__vehicle_type__name').annotate(count=Count('id'))
    
    # --- Biểu đồ doughnut: Tỷ lệ xe đang đỗ/còn trống theo khu vực ---
    parking_area_usage = []
    for area in ParkingArea.objects.all():
        occupied = area.current_occupancy
        free = max(0, area.max_capacity - occupied)
        parking_area_usage.append({
            'area': area.name,
            'occupied': occupied,
            'free': free,
            'usage_percentage': (occupied / area.max_capacity * 100) if area.max_capacity > 0 else 0
        })
    
    context = {
        'vehicles_in_parking': vehicles_in_parking,
        'revenue_month': f"{revenue_month:,.0f} VND" if revenue_month else "0 VND",
        'total_free_slots': total_free_slots,
        'usage_percentage': round(usage_percentage, 2),
        'recent_activities': recent_activities,
        'vehicles_in_out_by_day': vehicles_in_out_by_day,
        'vehicle_type_distribution': list(vehicle_type_distribution),
        'parking_area_usage': parking_area_usage,
    }
    return render(request, 'home.html', context)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import ParkingRecord

@login_required
def parking_history_view(request):
    query = request.GET.get('q', '')  # Lấy giá trị tìm kiếm từ thanh tìm kiếm
    page_number = request.GET.get('page', 1)  # Lấy số trang từ URL, mặc định là 1
    
    # Lấy danh sách bản ghi
    if query:
        parking_records = ParkingRecord.objects.filter(
            Q(vehicle__license_plate__icontains=query) | Q(ticket_code__icontains=query)
        ).select_related('vehicle__vehicle_type', 'parking_area').order_by('-check_in_time')
    else:
        parking_records = ParkingRecord.objects.select_related('vehicle__vehicle_type', 'parking_area').order_by('-check_in_time')
    
    # Phân trang
    paginator = Paginator(parking_records, 12)  # 12 bản ghi mỗi trang
    page_obj = paginator.get_page(page_number)
    
    # Chuyển danh sách bản ghi thành JSON cho cả AJAX và dữ liệu ban đầu
    records_data = [{
        'ticket_code': record.ticket_code,
        'license_plate': record.vehicle.license_plate,
        'vehicle_type': record.vehicle.vehicle_type.name,
        'parking_area': record.parking_area.name,
        'payment_status': 'Đã trả' if record.payment_status == 'paid' else 'Đang đỗ',
         'check_in_time': timezone.localtime(record.check_in_time).strftime('%H:%M %d/%m/%Y'),
        'check_out_time': timezone.localtime(record.check_out_time).strftime('%H:%M %d/%m/%Y') if record.check_out_time else '',

                'license_plate_image': record.vehicle.image if record.vehicle.image else None  # Sử dụng image URL

    } for record in page_obj.object_list]
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Yêu cầu AJAX
        return JsonResponse({'records': records_data})
    
    # Hiển thị trang ban đầu
    context = {
        'parking_records': page_obj.object_list,  # Danh sách bản ghi của trang hiện tại
        'records_data': records_data,
        'query': query,
        'page_obj': page_obj,  # Đối tượng phân trang
    }
    return render(request, 'parking_history.html', context)