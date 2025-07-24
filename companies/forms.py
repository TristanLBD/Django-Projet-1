from django import forms
from .models import Company, CompanyPhoto


class CompanyForm(forms.ModelForm):
    """Formulaire pour créer/modifier une entreprise"""

    class Meta:
        model = Company
        fields = [
            'name', 'description', 'address', 'phone',
            'email', 'website', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
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


class CompanyPhotoForm(forms.ModelForm):
    """Formulaire pour ajouter des photos à une entreprise"""

    class Meta:
        model = CompanyPhoto
        fields = ['image', 'caption', 'is_primary']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # Personnaliser le label de l'image
        self.fields['image'].label = 'Photo'
        self.fields['image'].help_text = 'Taille maximale : 5 MB. Formats acceptés : JPG, PNG, GIF'

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Vérifier la taille du fichier (5 MB max)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('L\'image est trop volumineuse. Taille maximale : 5 MB.')

            # Vérifier l'extension
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            import os
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    'Format d\'image non supporté. Formats acceptés : JPG, PNG, GIF'
                )

        return image
