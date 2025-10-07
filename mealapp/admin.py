from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.db.models import Sum,Q
from .models import MealSchedule, Bazar, Deposit,ExtraChargeNew
from .forms import MealScheduleFormSet, MealScheduleMultiDateForm
from django.db import models

class YearListFilterCharge(admin.SimpleListFilter):
    title = 'Year'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        years = ExtraChargeNew.objects.dates('date', 'year')
        return [(y.year, y.year) for y in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__year=self.value())
        return queryset


class MonthListFilterCharge(admin.SimpleListFilter):
    title = 'Month'
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        months = ExtraChargeNew.objects.dates('date', 'month')
        return [(m.month, m.strftime('%B')) for m in months]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__month=self.value())
        return queryset


@admin.register(ExtraChargeNew)
class ExtraChargeAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'charge_type', 'amount', 'details')  # use date instead of year/month
    list_filter = ('user', 'charge_type', YearListFilterCharge, MonthListFilterCharge)
    search_fields = ('user__username', 'details')
    ordering = ('-date', 'user')  # order by date instead of year/month
    change_list_template = "admin/mealapp/extracharge/change_list_charge.html"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset

            totals = qs.aggregate(
                total_current=Sum('amount', filter=Q(charge_type='current')),
                total_mowla=Sum('amount', filter=Q(charge_type='mowla')),
                total_others=Sum('amount', filter=Q(charge_type='others')),
            )

            totals['total_current'] = totals['total_current'] or 0
            totals['total_mowla'] = totals['total_mowla'] or 0
            totals['total_others'] = totals['total_others'] or 0
            totals['grand_total'] = (
                totals['total_current'] +
                totals['total_mowla'] +
                totals['total_others']
            )

            response.context_data['totals'] = totals
        except (AttributeError, KeyError):
            pass

        return response



class YearListFilterBazar(admin.SimpleListFilter):
    title = 'Year'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        years = Bazar.objects.dates('date', 'year')
        return [(y.year, y.year) for y in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__year=self.value())
        return queryset


class MonthListFilterBazar(admin.SimpleListFilter):
    title = 'Month'
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        months = Bazar.objects.dates('date', 'month')
        return [(m.month, m.strftime('%B')) for m in months]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__month=self.value())
        return queryset

@admin.register(Bazar)
class BazarAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'amount', 'details')
    list_filter = (
        'user',
        ('date', admin.DateFieldListFilter),
        YearListFilterBazar,
        MonthListFilterBazar,
    )
    ordering = ('-date', 'user')
    search_fields = ('user__username', 'details')

    # ✅ Custom template for this model only
    change_list_template = "admin/mealapp/bazar/change_list_bazar.html"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data['cl'].queryset

            totals = qs.aggregate(total_amount=Sum('amount'))
            totals['total_amount'] = totals['total_amount'] or 0

            response.context_data['totals'] = totals
        except (AttributeError, KeyError):
            pass

        return response




class YearListFilterDeposit(admin.SimpleListFilter):
    title = 'Year'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        years = Deposit.objects.dates('date', 'year')
        return [(y.year, y.year) for y in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__year=self.value())
        return queryset


class MonthListFilterDeposit(admin.SimpleListFilter):
    title = 'Month'
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        months = Deposit.objects.dates('date', 'month')
        return [(m.month, m.strftime('%B')) for m in months]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__month=self.value())
        return queryset


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'amount')
    list_filter = (
        'user',
        ('date', admin.DateFieldListFilter),
        YearListFilterDeposit,
        MonthListFilterDeposit,
    )
    ordering = ('-date', 'user')
    search_fields = ('user__username','date')

    # ✅ Custom template for this model only
    change_list_template = "admin/mealapp/deposit/change_list_deposit.html"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data['cl'].queryset

            totals = qs.aggregate(total_amount=Sum('amount'))
            totals['total_amount'] = totals['total_amount'] or 0

            response.context_data['totals'] = totals
        except (AttributeError, KeyError):
            pass

        return response
class YearListFilter(admin.SimpleListFilter):
    title = 'Year'
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        years = MealSchedule.objects.dates('date', 'year')
        return [(y.year, y.year) for y in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__year=self.value())
        return queryset


class MonthListFilter(admin.SimpleListFilter):
    title = 'Month'
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        months = MealSchedule.objects.dates('date', 'month')
        return [(m.month, m.strftime('%B')) for m in months]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__month=self.value())
        return queryset


@admin.register(MealSchedule)
class MealScheduleAdmin(ModelAdmin):
    list_display = ('user', 'date', 'noon', 'night', 'guest_noon', 'guest_night')
    list_filter = (
        'user',
        ('date', admin.DateFieldListFilter),
        YearListFilter, MonthListFilter
    )
    ordering = ('-date', 'user')   
    search_fields = ('user__username',)

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data['cl'].queryset

            totals = qs.aggregate(
                total_noon=Sum('noon'),
                total_night=Sum('night'),
                total_guest_noon=Sum('guest_noon'),
                total_guest_night=Sum('guest_night'),
            )

            # Noon/Night are booleans → Sum will count True as 1
            totals['total_noon'] = totals['total_noon'] or 0
            totals['total_night'] = totals['total_night'] or 0
            totals['total_guest_noon'] = totals['total_guest_noon'] or 0
            totals['total_guest_night'] = totals['total_guest_night'] or 0
            totals['grand_total'] = (
                (totals['total_noon'] or 0) +
                (totals['total_night'] or 0) +
                (totals['total_guest_noon'] or 0) +
                (totals['total_guest_night'] or 0)
            )
            response.context_data['totals'] = totals
        except (AttributeError, KeyError):
            pass

        return response
