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
def check_in(request):
    return render(request, 'check_in.html')

@login_required
def check_out(request):
    return render(request, 'check_out.html')

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

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import VehicleType
from .forms import VehicleTypeForm

@login_required
@user_passes_test(lambda u: u.is_superuser)
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

from django.shortcuts import render, redirect
from .models import VehicleType, ParkingArea
from .forms import ParkingAreaForm  # Giả sử bạn có form này

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

# parking/views.py
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from .recognizer import detect_license_plate

@csrf_exempt
def recognize_license_plate(request):
    if request.method == 'POST' and request.FILES.get('frame'):
        frame = request.FILES['frame']
        file_path = default_storage.save('temp/webcam_frame.jpg', frame)
        full_path = os.path.join(default_storage.location, file_path)

        # Process frame with ALPR
        license_plate = detect_license_plate(full_path)

        # Clean up
        default_storage.delete(file_path)

        if license_plate:
            return JsonResponse({'license_plate': license_plate})
        return JsonResponse({'error': 'No license plate detected'}, status=200)  # Use 200 to avoid breaking the loop
    return JsonResponse({'error': 'Invalid request'}, status=400)

import logging
from django.http import JsonResponse
from django.db.models import F
from .models import ParkingArea, VehicleType,ParkingRecord

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

@login_required
def vehicle_check_in(request):
    if request.method == 'POST':
        license_plate = request.POST.get('license_plate').strip().upper()
        vehicle_type_id = request.POST.get('vehicle_type')
        area_id = request.POST.get('parking_area')

        if not (license_plate and vehicle_type_id and area_id):
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin.')
            return redirect('vehicle_check_in')

        # Lấy loại xe và khu vực
        try:
            vehicle_type = VehicleType.objects.get(id=vehicle_type_id)
            parking_area = ParkingArea.objects.get(id=area_id)
        except (VehicleType.DoesNotExist, ParkingArea.DoesNotExist):
            messages.error(request, 'Loại xe hoặc khu vực không hợp lệ.')
            return redirect('vehicle_check_in')

        # Kiểm tra sức chứa khu vực
        if parking_area.current_occupancy >= parking_area.max_capacity:
            messages.error(request, 'Khu vực này đã đầy.')
            return redirect('vehicle_check_in')

        # Tạo hoặc lấy xe
        vehicle, created = Vehicle.objects.get_or_create(
            license_plate=license_plate,
            defaults={'vehicle_type': vehicle_type}
        )

        if not created and vehicle.vehicle_type != vehicle_type:
            vehicle.vehicle_type = vehicle_type
            vehicle.save()

        staff = request.user
        # Tăng số lượng xe trong khu vực
        parking_area.current_occupancy += 1
        parking_area.save()

        # Ghi nhận lịch sử nhận xe
        ParkingRecord.objects.create(
            vehicle=vehicle,
            parking_area=parking_area,
            staff=staff,
            check_in_time=timezone.now()
        )

        messages.success(request, f"Đã nhận xe biển số {license_plate}")
        return redirect('vehicle_check_in')

    # GET request
    vehicle_types = VehicleType.objects.all()
    recent_records = ParkingRecord.objects.select_related('vehicle', 'parking_area', 'staff')\
                                          .order_by('-check_in_time')[:5]

    return render(request, 'check_in.html', {
        'vehicle_types': vehicle_types,
        'recent_records': recent_records,
    })