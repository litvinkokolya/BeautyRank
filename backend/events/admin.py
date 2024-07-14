from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget

from users.models import User

from .models import *


@admin.register(
    Category,
    NominationAttribute,
    EventCategory,
)
class DefaultEventAdmin(admin.ModelAdmin):
    pass


class NominationAttributeInline(admin.TabularInline):
    model = NominationAttribute


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    readonly_fields = ["finished"]
    actions = ["make_finished", "clean_champ"]
    list_display = ["name", "finished"]

    @admin.action(description="Завершить чемп")
    def make_finished(self, request, queryset):
        queryset.update(finished=True)
        for event in queryset:
            event.result = event.generate_result()
            event.save()

    @admin.action(description="Удалить связанные файлы/объекты")
    def clean_champ(self, request, queryset):
        for event in queryset:
            for photo in MemberNominationPhoto.objects.filter(
                member_nomination__member__event=event
            ):
                photo.delete()
            Result.objects.filter(member_nomination__member__event=event).delete()
            MemberNomination.objects.filter(member__event=event).delete()
            Member.objects.filter(event=event).delete()
            CategoryNomination.objects.filter(event_category__event=event).delete()
            EventCategory.objects.filter(event=event).delete()


@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    inlines = [NominationAttributeInline]


class MemberNominationInline(admin.TabularInline):
    model = MemberNomination
    exclude = ["url_video", "url_message_video"]


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]
    inlines = [MemberNominationInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super(MemberAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["user"].queryset = User.objects.filter(is_staff=False)
        return form


@admin.register(CategoryNomination)
class CategoryNominationAdmin(admin.ModelAdmin):
    filter_horizontal = ("event_staff",)
    list_display = ("event_category", "nomination")
    list_display_links = ("event_category", "nomination")
    ordering = ["event_category", "nomination"]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if change:
            mn = MemberNomination.objects.filter(category_nomination=form.instance)
            list(map(lambda x: x.save(), mn))


@admin.register(MemberNomination)
class MemberNominationAdmin(admin.ModelAdmin):
    list_display = ("id", "member", "category_nomination")
    list_display_links = ("id", "member", "category_nomination")
    ordering = ["id"]


@admin.register(MemberNominationPhoto)
class MemberNominationPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "member_nomination", "photo")
    list_display_links = ("id", "member_nomination", "photo")
    ordering = ["member_nomination"]


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("id", "event_staff", "score", "member_nomination")
    list_display_links = ("id", "event_staff", "score", "member_nomination")
    ordering = ["event_staff"]


admin.site.site_title = "Админ-панель BeautyRank"
admin.site.site_header = "Админ-панель BeautyRank"
