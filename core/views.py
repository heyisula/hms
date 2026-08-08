import json
from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.utils import timezone
from django.db.models import Count

from .models import Appointment, Doctor, Patient


def login_view(request):
    """Render login page; authenticate and redirect on POST."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Honour ?next= if present, otherwise go to dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    """Log out and redirect to login page."""
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard_view(request):
    """Main dashboard with live stats pulled from the database."""
    today = timezone.localdate()
    now = timezone.localtime()

    # Determine greeting
    hour = now.hour
    if hour < 12:
        time_of_day = 'morning'
    elif hour < 17:
        time_of_day = 'afternoon'
    else:
        time_of_day = 'evening'

    # --- REALTIME LINE CHART DATA (Last 7 Days) ---
    last_7_dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    chart_labels = [d.strftime('%b %d') for d in last_7_dates]
    
    appointments_last_7_days = Appointment.objects.filter(
        date__gte=last_7_dates[0],
        date__lte=today
    ).values('date').annotate(count=Count('id'))
    
    data_dict = {d: 0 for d in last_7_dates}
    for entry in appointments_last_7_days:
        data_dict[entry['date']] = entry['count']
        
    chart_data = [data_dict[d] for d in last_7_dates]

    # --- REALTIME BAR CHART DATA (Blood Group) ---
    patients_by_blood = Patient.objects.values('blood_group').annotate(count=Count('id')).exclude(blood_group='')
    bg_labels = [entry['blood_group'] for entry in patients_by_blood]
    bg_data = [entry['count'] for entry in patients_by_blood]

    # --- REALTIME HORIZONTAL BAR CHART DATA (Doctors by Dept) ---
    doctors_by_dept = Doctor.objects.values('department__name').annotate(count=Count('id'))
    dept_labels = [entry['department__name'] or 'Unassigned' for entry in doctors_by_dept]
    dept_data = [entry['count'] for entry in doctors_by_dept]

    context = {
        'today': today,
        'time_of_day': time_of_day,
        'total_patients': Patient.objects.count(),
        'todays_appointments': Appointment.objects.filter(date=today).count(),
        'active_doctors': Doctor.objects.filter(is_active=True).count(),
        
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        
        'status_completed': Appointment.objects.filter(status='completed').count(),
        'status_scheduled': Appointment.objects.filter(status='scheduled').count(),
        'status_cancelled': Appointment.objects.filter(status='cancelled').count(),

        'bg_labels': json.dumps(bg_labels),
        'bg_data': json.dumps(bg_data),
        'dept_labels': json.dumps(dept_labels),
        'dept_data': json.dumps(dept_data),
    }
    return render(request, 'core/dashboard.html', context)
