from django.contrib import admin

from .models import ManagerProfile, RepairRequest, Status, StatusChangeLog
from .services import log_status_change


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "sort_order", "is_terminal")
    ordering = ("sort_order",)
    search_fields = ("title", "slug")


class StatusChangeLogInline(admin.TabularInline):
    model = StatusChangeLog
    extra = 0
    can_delete = False
    readonly_fields = ("old_status", "new_status", "changed_by", "comment", "created_at")
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(RepairRequest)
class RepairRequestAdmin(admin.ModelAdmin):
    list_display = ("code", "customer_name", "customer", "phone", "device", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("code", "customer_name", "customer__username", "customer__email", "phone", "device")
    readonly_fields = ("code", "created_at", "updated_at")
    raw_id_fields = ("customer",)
    autocomplete_fields = ("status",)
    inlines = (StatusChangeLogInline,)

    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            old_status = RepairRequest.objects.select_related("status").get(pk=obj.pk).status

        super().save_model(request, obj, form, change)

        if change and old_status.pk != obj.status_id:
            log_status_change(obj, old_status=old_status, changed_by=request.user, comment="Статус изменен в админке")
        elif not change:
            log_status_change(obj, changed_by=request.user, comment="Заявка создана в админке")


@admin.register(StatusChangeLog)
class StatusChangeLogAdmin(admin.ModelAdmin):
    list_display = ("repair_request", "old_status", "new_status", "changed_by", "created_at")
    list_filter = ("new_status", "created_at")
    search_fields = ("repair_request__code", "repair_request__customer_name", "changed_by__username")
    readonly_fields = ("repair_request", "old_status", "new_status", "changed_by", "comment", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "phone")
    search_fields = ("full_name", "user__username", "user__email")
