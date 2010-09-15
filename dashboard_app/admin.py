"""
Administration interface of the Dashboard application
"""

from django import forms
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

from dashboard_app.models import (
        Bundle,
        BundleDeserializationError,
        BundleStream,
        HardwareDevice,
        NamedAttribute,
        SoftwarePackage,
        Test,
        TestCase,
        TestResult,
        TestRun,
        )


class BundleAdmin(admin.ModelAdmin):

    def bundle_stream_pathname(self, bundle):
        return bundle.bundle_stream.pathname
    bundle_stream_pathname.short_description = _("Bundle stream")

    list_display = ('bundle_stream_pathname', 'content_filename',
            'uploaded_by', 'uploaded_on', 'is_deserialized')
    date_hierarchy = 'uploaded_on'
    fieldsets = (
            ('Document', {
                'fields': ('content', 'content_filename')}),
            ('Upload Details', {
                'fields': ('bundle_stream', 'uploaded_by')}),
            )


class BundleDeserializationErrorAdmin(admin.ModelAdmin):
    pass


class BundleStreamAdminForm(forms.ModelForm):
    class Meta:
        model = BundleStream

    def clean(self):
        cleaned_data = self.cleaned_data
        if (cleaned_data.get('user', '') is not None and
                cleaned_data.get('group') is not None):
            raise forms.ValidationError('BundleStream cannot have both user '
                    'and name set at the same time')
        return super(BundleStreamAdminForm, self).clean()


class BundleStreamAdmin(admin.ModelAdmin):
    form = BundleStreamAdminForm
    list_display = ('user', 'group', 'slug', 'name', 'pathname')
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
            (None, {
                'fields': ('name', 'slug')}),
            ('Ownership', {
                'fields': ('user', 'group')}),
            )


class SoftwarePackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'version')
    search_fields = ('name', 'version')


class HardwareDeviceAdmin(admin.ModelAdmin):
    class NamedAttributeInline(generic.GenericTabularInline):
        model = NamedAttribute
    list_display = ('description', 'device_type')
    search_fields = ('description',)
    inlines = [NamedAttributeInline]


class TestCaseAdmin(admin.ModelAdmin):
    pass


class TestAdmin(admin.ModelAdmin):
    pass


class TestResultAdmin(admin.ModelAdmin):
    class NamedAttributeInline(generic.GenericTabularInline):
        model = NamedAttribute
    list_display = ('test_run', 'test_case', 'result', 'measurement')
    list_filter = ('test_run', 'test_case', 'result')
    inlines = [NamedAttributeInline]


class TestRunAdmin(admin.ModelAdmin):
    class NamedAttributeInline(generic.GenericTabularInline):
        model = NamedAttribute
    list_display = ('analyzer_assigned_uuid',
                    'analyzer_assigned_date', 'import_assigned_date')
    inlines = [NamedAttributeInline]


admin.site.register(Bundle, BundleAdmin)
admin.site.register(BundleDeserializationError, BundleDeserializationErrorAdmin)
admin.site.register(BundleStream, BundleStreamAdmin)
admin.site.register(HardwareDevice, HardwareDeviceAdmin)
admin.site.register(SoftwarePackage, SoftwarePackageAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(TestCase, TestCaseAdmin)
admin.site.register(TestResult, TestResultAdmin)
admin.site.register(TestRun, TestRunAdmin)
