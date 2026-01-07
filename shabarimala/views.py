from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect,get_object_or_404 
# FILE UPLOAD AND VIEW
from  django.core.files.storage import FileSystemStorage
# SESSION
from django.conf import settings
from django.utils import timezone
from .models import *
from django.contrib import messages
from django.db.models import Sum, Count, F

def first(request):
    return render(request,'index.html')

def index(request):
    return render(request,'index.html')


def reg(request):
    return render(request,'register.html')


def addreg(request):
    if request.method=="POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        password=request.POST.get('password')
        ins=register(name=name,email=email,phone=phone,password=password)
        ins.save()
    return render(request,'register.html',{'message':"Successfully Registerd"})    




def login(request):
     return render(request,'login.html')
    



def addlogin(request):
    email=request.POST.get('email')
    password=request.POST.get('password')
    if email=='admin@gmail.com' and password =='admin':
        request.session['logint']=email
        return render(request,'index.html')
    elif register.objects.filter(email=email,password=password).exists():
        user=register.objects.get(email=email,password=password)
        request.session['uid']=user.id
        return render(request,'index.html')
    elif Police.objects.filter(email=email,password=password).exists():
        police=Police.objects.get(email=email,password=password)
        request.session['police_id']=police.id
        request.session['police_name']=police.name
        request.session['police_rank']=police.rank
        return render(request,'index.html')
    elif MedicalStaff.objects.filter(email=email,password=password).exists():
        medical_staff=MedicalStaff.objects.get(email=email,password=password)
        request.session['medical_staff_id']=medical_staff.id
        request.session['medical_staff_name']=medical_staff.name
        request.session['medical_staff_specialization']=medical_staff.specialization
        return render(request,'index.html')
    else:
        return render(request,'login.html')
    



def logout(request):
    session_keys=list(request.session.keys())
    for key in session_keys:
          del request.session[key]
    return redirect(first)

def viewuser(request):
    data=register.objects.all()
    return render(request,'viewuser.html',{'data':data})



def upload(request):
    if request.method=="POST" and request.FILES['myfile']:
        myfile=request.FILES['myfile']
        fs=FileSystemStorage()
        filename=fs.save(myfile.name,myfile)
        uploaded_file_url=fs.url(filename)
        return render(request,'upload.html',{'uploaded_file_url':uploaded_file_url})
    return render(request,'upload.html')


def add_slot(request):
    if request.method == "POST":
        date = request.POST.get('date')
        route = request.POST.get('route')
        number_of_slots = request.POST.get('number_of_slots')
        slot = Slot(date=date, route=route, number_of_slots=number_of_slots)
        slot.save()
        messages.success(request, "Slot added successfully!")
        return redirect('add_slot')
    
    # Get slots grouped by date and route with total slots
    slots = Slot.objects.values('date', 'route').annotate(
        total_slots=Sum('number_of_slots')
    ).order_by('date', 'route')
    
    # Get daily totals across all routes
    daily_totals = Slot.objects.values('date').annotate(
        daily_total=Sum('number_of_slots')
    ).order_by('date')
    
    return render(request, 'add_slot.html', {'slots': slots, 'daily_totals': daily_totals})


def add_weather(request):
    if request.method == "POST":
        date = request.POST.get('date')
        low_temperature = request.POST.get('low_temperature')
        high_temperature = request.POST.get('high_temperature')
        windspeed = request.POST.get('windspeed')
        description = request.POST.get('description')
        weather = Weather(date=date, low_temperature=low_temperature, 
                         high_temperature=high_temperature, windspeed=windspeed, 
                         description=description)
        weather.save()
        messages.success(request, "Weather details added successfully!")
        return redirect('add_weather')
    
    # Get all weather records
    weather_records = Weather.objects.all().order_by('-date')
    
    return render(request, 'add_weather.html', {'weather_records': weather_records})


def book_slot(request):
    if not request.session.get('uid'):
        return redirect('login')
    
    user_id = request.session['uid']
    user = register.objects.get(id=user_id)
    
    # Check if user already has a booking
    existing_booking = Booking.objects.filter(user=user).first()
    
    selected_date = request.GET.get('date')
    available_routes = None
    
    if selected_date:
        # Get available routes for the selected date
        available_routes = Slot.objects.filter(date=selected_date).annotate(
            booked_count=Count('booking'),
            available_slots=F('number_of_slots') - Count('booking')
        ).filter(
            number_of_slots__gt=models.F('booked_count')
        ).order_by('route')
    
    if request.method == "POST":
        if existing_booking:
            messages.error(request, "You already have a booking. You can only book one slot.")
            return redirect('book_slot')
        
        slot_id = request.POST.get('slot_id')
        aadhar_name = request.POST.get('aadhar_name')
        aadhar_number = request.POST.get('aadhar_number')
        date_of_birth = request.POST.get('date_of_birth')
        
        # Validate required fields
        if not aadhar_name or not aadhar_number or not date_of_birth:
            messages.error(request, "All Aadhar details are required.")
            return redirect(f"{request.path}?date={selected_date}")
        
        # Validate Aadhar number (should be 12 digits)
        if len(aadhar_number) != 12 or not aadhar_number.isdigit():
            messages.error(request, "Please enter a valid 12-digit Aadhar number.")
            return redirect(f"{request.path}?date={selected_date}")
        
        try:
            slot = Slot.objects.get(id=slot_id)
            
            # Check if slot is still available
            booked_count = Booking.objects.filter(slot=slot).count()
            if booked_count >= slot.number_of_slots:
                messages.error(request, "This slot is no longer available.")
                return redirect(f"{request.path}?date={selected_date}")
            
            # Create booking
            booking = Booking(
                user=user, 
                slot=slot, 
                aadhar_name=aadhar_name,
                aadhar_number=aadhar_number,
                date_of_birth=date_of_birth
            )
            booking.save()
            messages.success(request, f"Slot booked successfully for {slot.date} - {slot.route}")
            return redirect('book_slot')
            
        except Slot.DoesNotExist:
            messages.error(request, "Invalid slot selection.")
            return redirect(f"{request.path}?date={selected_date}")
    
    # Get all available dates (dates that have available slots)
    available_dates = Slot.objects.annotate(
        booked_count=Count('booking')
    ).filter(
        number_of_slots__gt=models.F('booked_count')
    ).values_list('date', flat=True).distinct().order_by('date')
    
    context = {
        'available_dates': available_dates,
        'selected_date': selected_date,
        'available_routes': available_routes,
        'existing_booking': existing_booking,
    }
    
    return render(request, 'book_slot.html', context)


def view_weather(request):
    if not request.session.get('uid'):
        messages.error(request, "Please login to view weather information.")
        return redirect('login')
    
    # Get all weather data ordered by date (newest first)
    weather_data = Weather.objects.all().order_by('-date')
    
    context = {
        'weather_data': weather_data,
    }
    
    return render(request, 'view_weather.html', context)


def view_booking(request):
    if not request.session.get('logint') and not request.session.get('police_id'):
        messages.error(request, "Please login to view bookings.")
        return redirect('login')
    
    # Get all bookings with related user and slot information
    bookings = Booking.objects.select_related('user', 'slot').order_by('-booking_date')
    
    # Calculate total number of bookings
    total_bookings = bookings.count()
    
    # Get slot availability information
    slot_availability = Slot.objects.annotate(
        booked_count=Count('booking')
    ).values('date', 'route', 'number_of_slots', 'booked_count').order_by('date', 'route')
    
    # Calculate slots left for each slot
    for slot_info in slot_availability:
        slot_info['slots_left'] = slot_info['number_of_slots'] - slot_info['booked_count']
    
    context = {
        'bookings': bookings,
        'total_bookings': total_bookings,
        'slot_availability': slot_availability,
    }
    
    return render(request, 'view_booking.html', context)


def add_police(request):
    if not request.session.get('logint'):
        messages.error(request, "Please login as admin to add police.")
        return redirect('login')
    
    return render(request, 'add_police.html')


def add_police_post(request):
    if not request.session.get('logint'):
        messages.error(request, "Please login as admin to add police.")
        return redirect('login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        badge_number = request.POST.get('badge_number')
        station = request.POST.get('station')
        rank = request.POST.get('rank')
        
        # Validate required fields
        if not all([name, email, phone, password, badge_number, station, rank]):
            messages.error(request, "All fields are required.")
            return redirect('add_police')
        
        # Check if email or badge number already exists
        if Police.objects.filter(email=email).exists():
            messages.error(request, "A police officer with this email already exists.")
            return redirect('add_police')
        
        if Police.objects.filter(badge_number=badge_number).exists():
            messages.error(request, "A police officer with this badge number already exists.")
            return redirect('add_police')
        
        # Create police officer
        police = Police(
            name=name,
            email=email,
            phone=phone,
            password=password,
            badge_number=badge_number,
            station=station,
            rank=rank
        )
        police.save()
        
        messages.success(request, f"Police officer {name} added successfully!")
        return redirect('add_police')
    
    return redirect('add_police')


def add_emergency(request):
    if not request.session.get('police_id'):
        messages.error(request, "Please login as police to report emergencies.")
        return redirect('login')
    
    return render(request, 'add_emergency.html')


def add_emergency_post(request):
    if not request.session.get('police_id'):
        messages.error(request, "Please login as police to report emergencies.")
        return redirect('login')
    
    if request.method == 'POST':
        emergency_type = request.POST.get('emergency_type')
        description = request.POST.get('description')
        location = request.POST.get('location')
        contact_number = request.POST.get('contact_number')
        medical_help_needed = request.POST.get('medical_help_needed') == 'on'
        medical_details = request.POST.get('medical_details') if medical_help_needed else ''
        
        # Validate required fields
        if not all([emergency_type, description, location, contact_number]):
            messages.error(request, "All fields are required.")
            return redirect('add_emergency')
        
        # Get the police officer reporting the emergency
        police_id = request.session.get('police_id')
        police = Police.objects.get(id=police_id)
        
        # Create emergency report
        emergency = Emergency(
            reporter=police,  # Police officer is the reporter
            emergency_type=emergency_type,
            description=description,
            location=location,
            contact_number=contact_number,
            medical_help_needed=medical_help_needed,
            medical_details=medical_details,
            status='pending'
        )
        emergency.save()
        
        messages.success(request, f"Emergency reported successfully! Emergency ID: {emergency.id}")
        return redirect('add_emergency')
    
    return redirect('add_emergency')


def view_emergency(request):
    if not request.session.get('logint') and not request.session.get('medical_staff_id'):
        messages.error(request, "Please login to view emergencies.")
        return redirect('login')
    
    # Get all emergencies with related reporter (police) information
    emergencies = Emergency.objects.select_related('reporter', 'responded_by').order_by('-reported_at')
    
    # Calculate statistics
    total_emergencies = emergencies.count()
    pending_emergencies = emergencies.filter(status='pending').count()
    responding_emergencies = emergencies.filter(status='responding').count()
    resolved_emergencies = emergencies.filter(status='resolved').count()
    
    context = {
        'emergencies': emergencies,
        'total_emergencies': total_emergencies,
        'pending_emergencies': pending_emergencies,
        'responding_emergencies': responding_emergencies,
        'resolved_emergencies': resolved_emergencies,
    }
    
    return render(request, 'view_emergency.html', context)


def view_response(request):
    if not request.session.get('police_id'):
        messages.error(request, "Please login as police to view responses.")
        return redirect('login')
    
    police = Police.objects.get(id=request.session['police_id'])
    
    # Get emergencies reported by this police officer
    emergencies = Emergency.objects.filter(reporter=police).select_related('reporter', 'responded_by', 'medical_staff_assigned').order_by('-reported_at')
    
    # Calculate statistics for this police officer's emergencies
    total_emergencies = emergencies.count()
    pending_emergencies = emergencies.filter(status='pending').count()
    responding_emergencies = emergencies.filter(status='responding').count()
    resolved_emergencies = emergencies.filter(status='resolved').count()
    
    context = {
        'emergencies': emergencies,
        'total_emergencies': total_emergencies,
        'pending_emergencies': pending_emergencies,
        'responding_emergencies': responding_emergencies,
        'resolved_emergencies': resolved_emergencies,
        'police_name': police.name,
    }
    
    return render(request, 'view_response.html', context)


def respond_emergency(request, emergency_id):
    if not request.session.get('police_id') and not request.session.get('medical_staff_id'):
        messages.error(request, "Please login to respond to emergencies.")
        return redirect('login')
    
    try:
        emergency = Emergency.objects.get(id=emergency_id)
    except Emergency.DoesNotExist:
        messages.error(request, "Emergency not found.")
        return redirect('view_emergency')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if request.session.get('police_id'):
            # Police response - police can only resolve or cancel emergencies they reported
            police = Police.objects.get(id=request.session['police_id'])
            
            if action == 'resolve':
                emergency.status = 'resolved'
                emergency.resolved_at = timezone.now()
                emergency.response_notes = notes
                messages.success(request, "Emergency marked as resolved.")
            elif action == 'cancel':
                emergency.status = 'cancelled'
                emergency.response_notes = notes
                messages.success(request, "Emergency cancelled.")
                
        elif request.session.get('medical_staff_id'):
            # Medical staff response - medical staff are primary responders
            medical_staff = MedicalStaff.objects.get(id=request.session['medical_staff_id'])
            
            if action == 'respond':
                emergency.medical_staff_assigned = medical_staff
                emergency.status = 'responding'
                emergency.medical_response_notes = notes
                emergency.medical_response_at = timezone.now()
                messages.success(request, "You have started responding to this medical emergency.")
            elif action == 'assign_medical':
                emergency.medical_staff_assigned = medical_staff
                emergency.medical_response_notes = notes
                emergency.medical_response_at = timezone.now()
                messages.success(request, "You have been assigned to this medical emergency.")
            elif action == 'medical_resolve':
                emergency.status = 'resolved'
                emergency.resolved_at = timezone.now()
                emergency.medical_response_notes = notes
                messages.success(request, "Medical emergency resolved.")
                
        emergency.save()
        return redirect('view_emergency')
    
    context = {
        'emergency': emergency,
    }
    return render(request, 'respond_emergency.html', context)


def add_medical_staff(request):
    if not request.session.get('logint'):
        messages.error(request, "Please login as admin to add medical staff.")
        return redirect('login')
    
    return render(request, 'add_medical_staff.html')


def add_medical_staff_post(request):
    if not request.session.get('logint'):
        messages.error(request, "Please login as admin to add medical staff.")
        return redirect('login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        license_number = request.POST.get('license_number')
        specialization = request.POST.get('specialization')
        hospital = request.POST.get('hospital')
        experience_years = request.POST.get('experience_years')
        
        # Validate required fields
        if not all([name, email, phone, password, license_number, specialization, hospital, experience_years]):
            messages.error(request, "All fields are required.")
            return redirect('add_medical_staff')
        
        # Check if email or license number already exists
        if MedicalStaff.objects.filter(email=email).exists():
            messages.error(request, "A medical staff member with this email already exists.")
            return redirect('add_medical_staff')
        
        if MedicalStaff.objects.filter(license_number=license_number).exists():
            messages.error(request, "A medical staff member with this license number already exists.")
            return redirect('add_medical_staff')
        
        try:
            experience_years = int(experience_years)
        except ValueError:
            messages.error(request, "Experience years must be a valid number.")
            return redirect('add_medical_staff')
        
        # Create medical staff member
        medical_staff = MedicalStaff(
            name=name,
            email=email,
            phone=phone,
            password=password,
            license_number=license_number,
            specialization=specialization,
            hospital=hospital,
            experience_years=experience_years
        )
        medical_staff.save()
        
        messages.success(request, f"Medical staff member {name} added successfully!")
        return redirect('add_medical_staff')
    
    return redirect('add_medical_staff')