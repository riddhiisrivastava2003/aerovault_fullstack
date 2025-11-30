from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse


def admin_login(request):
    # if already logged-in and staff, redirect to admin dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('adminpanel:dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            next_url = request.GET.get('next') or reverse('adminpanel:dashboard')
            return redirect(next_url)
        else:
            error = 'Invalid credentials or not an admin user.'
            messages.error(request, error)

    return render(request, 'adminpanel/login.html', {'error': error})


def admin_logout(request):
    logout(request)
    return redirect('adminpanel:login')
