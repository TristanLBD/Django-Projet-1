from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserProfile
from .forms import UserProfileForm
from companies.utils import is_employer, is_admin


class LoginView:
    """Vue pour la page de connexion"""

    def __init__(self):
        self.template_name = 'accounts/login.html'

    def get_success_url(self, user):
        """Détermine l'URL de redirection selon le type d'utilisateur"""
        if is_admin(user):
            return reverse_lazy('admin_dashboard')
        elif is_employer(user):
            return reverse_lazy('employer_dashboard')
        else:
            return reverse_lazy('user_dashboard')

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(self.get_success_url(request.user))

        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {user.username} !')
                return redirect(self.get_success_url(user))
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')

        return render(request, self.template_name, {'form': form})


def login_view(request):
    """Vue fonction pour la page de connexion"""
    view = LoginView()
    if request.method == 'GET':
        return view.get(request)
    elif request.method == 'POST':
        return view.post(request)


def logout_view(request):
    """Vue pour la déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('accounts:login')


def profile_detail(request):
    """Vue pour afficher le profil utilisateur"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    return render(request, 'accounts/profile_detail.html', {
        'user': request.user
    })


@login_required
def profile_edit(request):
    """Vue pour modifier le profil utilisateur"""
    if request.method == 'POST':
        # Formulaire pour les informations utilisateur
        user_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Profil mis à jour avec succès !')
            return redirect('accounts:profile_detail')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        user_form = UserProfileForm(instance=request.user.profile)

    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'user': request.user
    })
