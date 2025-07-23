from django.contrib import admin
from django.utils.html import format_html
from .models import Company, CompanyPhoto


class CompanyPhotoInline(admin.TabularInline):
    model = CompanyPhoto
    extra = 1
    fields = ['image', 'caption', 'is_primary']
    readonly_fields = ['uploaded_at']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'created_by', 'phone', 'email', 'is_active', 'created_at', 'photo_count'
    ]
    list_filter = ['is_active', 'created_at', 'created_by']
    search_fields = ['name', 'description', 'address', 'email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CompanyPhotoInline]

    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Coordonnées', {
            'fields': ('address', 'phone', 'email', 'website')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def photo_count(self, obj):
        return obj.photos.count()
    photo_count.short_description = "Nombre de photos"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)


@admin.register(CompanyPhoto)
class CompanyPhotoAdmin(admin.ModelAdmin):
    list_display = [
        'company', 'image_preview', 'caption', 'is_primary', 'uploaded_at'
    ]
    list_filter = ['is_primary', 'uploaded_at', 'company']
    search_fields = ['company__name', 'caption']
    readonly_fields = ['uploaded_at', 'image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "Aucune image"
    image_preview.short_description = "Aperçu"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company__created_by=request.user)
