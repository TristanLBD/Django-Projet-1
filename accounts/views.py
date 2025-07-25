from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserProfile
from .forms import UserProfileForm
from companies.utils import is_employer, is_admin


class LoginView(View):
    """Vue pour la page de connexion"""
    template_name = 'accounts/login.html'

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


class LogoutView(View):
    """Vue pour la déconnexion"""
    def get(self, request):
        logout(request)
        messages.success(request, 'Vous avez été déconnecté avec succès.')
        return redirect('accounts:login')


class ProfileDetailView(LoginRequiredMixin, TemplateView):
    """Vue pour afficher le profil utilisateur"""
    template_name = 'accounts/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Vue pour modifier le profil utilisateur"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile_detail')

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Profil mis à jour avec succès !')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Veuillez corriger les erreurs ci-dessous.')
        return super().form_invalid(form)
