from django import forms
from .models import Job, Application
from companies.models import Company


class JobForm(forms.ModelForm):
    """Formulaire pour créer/modifier une offre d'emploi"""

    class Meta:
        model = Job
        fields = [
            'title', 'company', 'description', 'requirements', 'benefits',
            'contract_type', 'experience_level', 'salary_min',
            'salary_max', 'location', 'is_remote', 'is_active', 'is_filled'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 5}),
            'benefits': forms.Textarea(attrs={'rows': 4}),
            'salary_min': forms.NumberInput(attrs={'min': 0}),
            'salary_max': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Appliquer les classes CSS selon le type de champ
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                # Les champs booléens n'ont pas besoin de la classe form-control
                continue
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

        # Filtrer les entreprises selon les permissions de l'utilisateur
        if user:
            from companies.utils import get_user_companies, is_admin
            if is_admin(user):
                # Les admins voient toutes les entreprises actives
                self.fields['company'].queryset = Company.objects.filter(is_active=True)
            else:
                # Les employeurs voient seulement leurs entreprises
                user_companies = get_user_companies(user)
                self.fields['company'].queryset = user_companies.filter(is_active=True)
        else:
            # Par défaut, toutes les entreprises actives
            self.fields['company'].queryset = Company.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')

        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError(
                'Le salaire minimum ne peut pas être supérieur au salaire maximum.'
            )

        return cleaned_data


class ApplicationForm(forms.ModelForm):
    """Formulaire pour postuler à une offre d'emploi"""

    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 8,
                'placeholder': 'Rédigez votre lettre de motivation...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # Personnaliser le label du CV
        self.fields['resume'].label = 'CV (PDF recommandé)'
        self.fields['resume'].help_text = 'Taille maximale : 5 MB. Formats acceptés : PDF, DOC, DOCX'

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Vérifier la taille du fichier (5 MB max)
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Le fichier est trop volumineux. Taille maximale : 5 MB.')

            # Vérifier l'extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            import os
            ext = os.path.splitext(resume.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    'Format de fichier non supporté. Formats acceptés : PDF, DOC, DOCX'
                )

        return resume
