from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import *
import datetime
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.db.models import Sum, F,Avg
from datetime import date, timedelta
from calendar import monthrange
import calendar
from datetime import date
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from decimal import Decimal
from calendar import month_name, monthrange

# check if user is admin/staff
def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
def dashboard(request):
    user = request.user
    today = date.today()

    # --- Total deposit till today (user) ---
    total_deposit = Deposit.objects.filter(user=user, date__lte=today).aggregate(total=Sum('amount'))['total'] or Decimal(0)

    # --- Total meals till today (user) ---
    meals = MealSchedule.objects.filter(user=user, date__lte=today)
    total_meals = sum([
        (1 if m.noon else 0) + (1 if m.night else 0) +
        m.guest_noon + m.guest_night
        for m in meals
    ])

    # --- Last month date range ---
    first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_last_month = today.replace(day=1) - timedelta(days=1)

    # --- Last month meals (user only) ---
    last_month_meals_qs = MealSchedule.objects.filter(user=user, date__range=(first_day_last_month, last_day_last_month))
    last_month_meals = sum([
        (1 if m.noon else 0) + (1 if m.night else 0) +
        m.guest_noon + m.guest_night
        for m in last_month_meals_qs
    ])
    last_month_meals = Decimal(last_month_meals)

    # --- Last month deposit (user only) ---
    last_month_deposit = Deposit.objects.filter(user=user, date__range=(first_day_last_month, last_day_last_month)).aggregate(total=Sum('amount'))['total'] or Decimal(0)

    # --- Global meal rate calculation (all users) ---
    last_month_bazar = Bazar.objects.filter(date__range=(first_day_last_month, last_day_last_month)).aggregate(total=Sum('amount'))['total'] or Decimal(0)

    all_meals_last_month_qs = MealSchedule.objects.filter(date__range=(first_day_last_month, last_day_last_month))
    all_meals_last_month = sum([
        (1 if m.noon else 0) + (1 if m.night else 0) +
        m.guest_noon + m.guest_night
        for m in all_meals_last_month_qs
    ])
    all_meals_last_month = Decimal(all_meals_last_month)

    meal_rate = last_month_bazar / all_meals_last_month if all_meals_last_month > 0 else Decimal(0)

    # --- Last month due/refund for this user ---
    last_month_due = last_month_deposit - (meal_rate * last_month_meals)

    # --- Average extra charge by type per member for last month ---
    total_members = User.objects.count() or 1  # avoid division by zero

    avg_extra_charges_qs = ExtraChargeNew.objects.filter(
        date__range=(first_day_last_month, last_day_last_month)
    ).values('charge_type').annotate(total_amount=Sum('amount'))

    avg_extra_charges_per_member = {
        item['charge_type']: (item['total_amount'] or Decimal(0)) / total_members
        for item in avg_extra_charges_qs
    }

    context = {
        'total_deposit': total_deposit,
        'total_meals': total_meals,
        'last_month_meals': last_month_meals,
        'last_month_deposit': last_month_deposit,
        'meal_rate': round(float(meal_rate), 2),
        'last_month_due': round(float(last_month_due), 2),
        'avg_extra_charges_per_member': avg_extra_charges_per_member,
        'first_day_last_month': first_day_last_month,
        'last_day_last_month': last_day_last_month,
    }

    return render(request, 'dashboard.html', context)
@login_required
def schedule_meal(request):
    today = datetime.date.today()

    if request.method == 'POST':
        date_str = request.POST['date']
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

        # ❌ no past dates
        if date < today:
            return render(request, 'schedule.html', {'error': "You cannot schedule past meals."})

        # ❌ no editing today if date == today
        if date == today and MealSchedule.objects.filter(user=request.user, date=today).exists():
            return render(request, 'schedule.html', {'error': "You cannot edit today's meals after the day started."})

        # get values
        noon = 'noon' in request.POST
        night = 'night' in request.POST
        guest_noon = int(request.POST.get('guest_noon', 0))
        guest_night = int(request.POST.get('guest_night', 0))

        MealSchedule.objects.update_or_create(
            user=request.user,
            date=date,
            defaults={
                'noon': noon,
                'night': night,
                'guest_noon': guest_noon,
                'guest_night': guest_night,
            }
        )
        return redirect('dashboard')

    return render(request, 'schedule.html')


# ✅ Admin only (bazar & deposit)
@login_required
@user_passes_test(is_admin)
def admin_bazar(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    months = {i: calendar.month_name[i] for i in range(1, 13)}

    bazar_list = Bazar.objects.filter(date__year=year, date__month=month).order_by('date')

    total_amount = bazar_list.aggregate(total=models.Sum('amount'))['total'] or 0

    context = {
        'bazar_list': bazar_list,
        'year': year,
        'month': month,
        'months': months,
        'total_amount': total_amount
    }
    return render(request, 'admin_bazar.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_deposit(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        amount = request.POST.get('amount')
        deposit_date = request.POST.get('date')

        user = User.objects.get(id=user_id)
        Deposit.objects.create(user=user, amount=amount, date=deposit_date)
        return redirect('admin_deposit')  # redirect back to deposit page

    users = User.objects.all()
    today = date.today()
    return render(request, 'add_deposit.html', {'users': users, 'today': today})


@login_required
@user_passes_test(is_admin)
def admin_deposit(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    months = {i: calendar.month_name[i] for i in range(1, 13)}

    deposits = Deposit.objects.filter(date__year=year, date__month=month).order_by('-date')
    total_amount = deposits.aggregate(total=models.Sum('amount'))['total'] or 0

    context = {
        'deposits': deposits,
        'year': year,
        'month': month,
        'months': months,
        'total_amount': total_amount
    }
    return render(request, 'admin_deposit.html', context)

def custom_logout(request):
    logout(request)
    return redirect('login')



@login_required
@user_passes_test(is_admin)
def meal_report_all(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    users = User.objects.all()
    days_in_month = monthrange(year, month)[1]

    # Initialize report_data: list of dicts per day
    report_data = []
    for day in range(1, days_in_month + 1):
        row = {'day': day, 'users': []}
        for user in users:
            row['users'].append({
                'username': user.username,
                'noon': 0,
                'night': 0,
                'guest_noon': 0,
                'guest_night': 0,
                'total': 0
            })
        report_data.append(row)

    # Fill meals
    meals = MealSchedule.objects.filter(date__year=year, date__month=month)
    for meal in meals:
        day_index = meal.date.day - 1
        for u in report_data[day_index]['users']:
            if u['username'] == meal.user.username:
                u['noon'] = 1 if meal.noon else 0
                u['night'] = 1 if meal.night else 0
                u['guest_noon'] = meal.guest_noon
                u['guest_night'] = meal.guest_night
                u['total'] = u['noon'] + u['night'] + u['guest_noon'] + u['guest_night']

    # Month dict for dropdown
    months = {i: month_name[i] for i in range(1, 13)}

    return render(request, 'meal_report_all.html', {
        'year': year,
        'month': month,
        'months': months,
        'users': users,
        'report_data': report_data
    })


@login_required
def meal_report(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    user = request.user  # logged-in user only
    days_in_month = monthrange(year, month)[1]

    # Initialize report_data: list of dicts per day
    report_data = []
    for day in range(1, days_in_month + 1):
        report_data.append({
            'day': day,
            'noon': 0,
            'night': 0,
            'guest_noon': 0,
            'guest_night': 0,
            'total': 0
        })

    # Fill meals
    meals = MealSchedule.objects.filter(user=user, date__year=year, date__month=month)
    for meal in meals:
        day_index = meal.date.day - 1
        report_data[day_index]['noon'] = 1 if meal.noon else 0
        report_data[day_index]['night'] = 1 if meal.night else 0
        report_data[day_index]['guest_noon'] = meal.guest_noon
        report_data[day_index]['guest_night'] = meal.guest_night
        report_data[day_index]['total'] = (report_data[day_index]['noon'] +
                                           report_data[day_index]['night'] +
                                           report_data[day_index]['guest_noon'] +
                                           report_data[day_index]['guest_night'])

    months = {i: month_name[i] for i in range(1, 13)}

    return render(request, 'meal_report.html', {
        'year': year,
        'month': month,
        'months': months,
        'report_data': report_data,
        'user': user,
        'days_in_month': days_in_month
    })


@user_passes_test(is_admin)
def add_bazar(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        amount = request.POST.get('amount')
        details = request.POST.get('details')
        bazar_date = request.POST.get('date')

        user = User.objects.get(id=user_id) if user_id else None

        Bazar.objects.create(
            user=user,
            amount=amount,
            details=details,
            date=bazar_date
        )
        return redirect('admin_bazar')

    users = User.objects.all()
    today = date.today()
    return render(request, 'add_bazar.html', {'users': users, 'today': today})



@login_required
def member_report_all(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    months = {i: calendar.month_name[i] for i in range(1, 13)}
    users = User.objects.all()

    # Total Bazar for the month
    total_bazar = Bazar.objects.filter(date__year=year, date__month=month).aggregate(total=Sum('amount'))['total'] or 0

    report_data = []

    for user in users:
        # Total deposit
        deposit = Deposit.objects.filter(user=user, date__year=year, date__month=month).aggregate(total=Sum('amount'))['total'] or 0

        # Total meals
        meals = MealSchedule.objects.filter(user=user, date__year=year, date__month=month)
        total_meal_count = sum([
            (1 if m.noon else 0) + (1 if m.night else 0) + m.guest_noon + m.guest_night
            for m in meals
        ])

        # Meal rate
        meal_rate = total_bazar / sum([m.noon + m.night + m.guest_noon + m.guest_night for m in MealSchedule.objects.filter(date__year=year, date__month=month)]) if total_bazar > 0 else 0

        # Extra charges
        extras = ExtraChargeNew.objects.filter(user=user, year=year, month=month)
        total_extra = sum([e.amount for e in extras])

        # Total expense
        total_expense = total_meal_count * meal_rate + total_extra

        # Due or refund
        due_or_refund = deposit - total_expense

        report_data.append({
            'user': user.username,
            'total_deposit': deposit,
            'total_meal': total_meal_count,
            'meal_rate': round(meal_rate, 2),
            'total_expense': round(total_expense, 2),
            'due_or_refund': round(due_or_refund, 2),
            'extras': extras
        })

    context = {
        'report_data': report_data,
        'year': year,
        'month': month,
        'months': months
    }

    return render(request, 'member_report_all.html', context)


@login_required
def member_report(request):
    user = request.user
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    months = {i: calendar.month_name[i] for i in range(1, 13)}

    # Total Bazar for the month
    total_bazar = Bazar.objects.filter(date__year=year, date__month=month).aggregate(total=Sum('amount'))['total'] or Decimal(0)

    # Total deposit
    deposit = Deposit.objects.filter(user=user, date__year=year, date__month=month).aggregate(total=Sum('amount'))['total'] or Decimal(0)

    # Total meals (for this user)
    meals = MealSchedule.objects.filter(user=user, date__year=year, date__month=month)
    total_meal_count = sum([
        (1 if m.noon else 0) + (1 if m.night else 0) + m.guest_noon + m.guest_night
        for m in meals
    ])

    # Global meal rate
    total_meals_all_users = sum([
        (1 if m.noon else 0) + (1 if m.night else 0) + m.guest_noon + m.guest_night
        for m in MealSchedule.objects.filter(date__year=year, date__month=month)
    ])
    meal_rate = total_bazar / total_meals_all_users if total_meals_all_users > 0 else Decimal(0)

    # Extra charges
    extras = ExtraChargeNew.objects.filter(user=user, date__year=year, date__month=month)
    total_extra = sum([e.amount for e in extras])

    # Extra charge summary (group by type)
    extra_summary = (
        ExtraChargeNew.objects
        .filter(user=user, date__year=year, date__month=month)
        .values('charge_type')
        .annotate(total=Sum('amount'))
    )

    # Total expense
    total_expense = total_meal_count * meal_rate + total_extra

    # Due or refund
    due_or_refund = deposit - total_expense

    context = {
        'user': user,
        'year': year,
        'month': month,
        'months': months,
        'total_deposit': deposit,
        'total_meal': total_meal_count,
        'meal_rate': round(meal_rate, 2),
        'total_expense': round(total_expense, 2),
        'due_or_refund': round(due_or_refund, 2),
        'extras': extras,
        'extra_summary': extra_summary,
    }

    return render(request, 'member_report.html', context)