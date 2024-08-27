from django.db import models
from django.db.models import constraints

from RateOnline.storage_backends import PrivateMediaStorage


class Category(models.Model):
    name = models.CharField(
        max_length=10,
        help_text="Введите название категории",
        verbose_name="Название категории",
    )

    description = models.TextField(
        max_length=100,
        help_text="Введите описание категории",
        verbose_name="Описание категории",
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Nomination(models.Model):
    name = models.CharField(
        max_length=50,
        help_text="Введите название номинации",
        verbose_name="Название номинации",
    )

    photos_conf = models.JSONField(default=dict)

    def get_photo_count(self):
        return len(self.photos_conf["before"]) + len(self.photos_conf["after"])

    class Meta:
        verbose_name = "Номинация"
        verbose_name_plural = "Номинации"
        ordering = ["id"]

    def __str__(self):
        return self.name


class NominationAttribute(models.Model):
    name = models.CharField(
        max_length=150,
        help_text="Введите название атрибута",
        verbose_name="Название атрибута",
    )
    nomination = models.ForeignKey(
        "Nomination",
        models.PROTECT,
        related_name="attribute",
        help_text="Выберите номинацию",
        verbose_name="Номинация",
    )
    max_score = models.IntegerField(
        default=5,
        help_text="Введите максимальную оценку",
        verbose_name="Максимальная оценка",
    )

    class Meta:
        verbose_name = "Атрибуты номинации"
        verbose_name_plural = "Атрибуты номинаций"

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(
        max_length=50,
        help_text="Введите название мероприятия",
        verbose_name="Название мероприятия",
    )
    image = models.ImageField(
        storage=PrivateMediaStorage,
        upload_to="event_photo/%Y/%m/%d",
        help_text="Выберите фото",
        verbose_name="Фото чемпионата",
    )
    owners = models.ManyToManyField(
        "users.User",
        blank=True,
        related_name="owner_events",
        help_text="Выберите организаторов",
        verbose_name="Организаторы",
    )
    finished = models.BooleanField(
        default=False,
        help_text="Поставьте галочку, если чемпионат завершился",
        verbose_name="Завершение чемпионата",
    )
    result = models.JSONField(
        default=dict,
        blank=True,
        help_text="Поле заполняется автоматически. Редактирование в крайнем случае",
        verbose_name="Результат чемпионата",
    )

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"

    def generate_result(self):
        categories = []
        for event_category in self.eventcategory_set.select_related("category"):
            nominations = []
            for nomination in event_category.categorynomination_set.select_related(
                "nomination"
            ):
                members = []
                for member in nomination.categ.select_related("member", "member__user"):
                    members.append(
                        {
                            "user_id": member.member.user.id,
                            "user_name": str(member.member.user),
                            "user_avatar": (
                                member.member.user.optimized_image.name
                                if member.member.user.optimized_image
                                else None
                            ),
                            "score": member.result_sum,
                        }
                    )
                nominations.append(
                    {"name": nomination.nomination.name, "members": members}
                )
            categories.append(
                {
                    "name": event_category.category.name,
                    "nominations": nominations,
                }
            )

        return {"name": self.name, "categories": categories}

    def get_winners_nominations(self):
        win_nominations = []
        event_categories = EventCategory.objects.filter(event=self.id)
        for event_category in event_categories:
            nominations_members = []
            category_nominations = CategoryNomination.objects.filter(
                event_category__category=event_category.category)
            for category_nomination in category_nominations:
                member_nominations = MemberNomination.objects.filter(
                    category_nomination=category_nomination
                )
                members = set(member_nominations.values_list("member", flat=True))
                top = []
                members_in_current_event = Member.objects.filter(event=self.id)

                for member in members:
                    result_all = sum(
                        Result.objects.filter(
                            member_nomination__member=member,
                            member_nomination__category_nomination=category_nomination,
                        ).values_list("score", flat=True)
                    )
                    top.append(
                        {
                            "member": members_in_current_event.get(pk=member),
                            "result_all": result_all,
                        }
                    )
                top = sorted(top, reverse=True, key=lambda x: x["result_all"])
                nominations_members.append(
                    {
                        "nomination": str(category_nomination.nomination),
                        "members": top,
                    }
                )
            win_nominations.append(
                {
                    'category': str(event_category.category.name),
                    'nominations': nominations_members
                }
            )
        return win_nominations

    def get_winners_categories(self):
        win_categories = []
        categories = Category.objects.filter(
            categories_in_EventCategoryModel__event=self.id
        )
        for category in categories:
            member_nominations = MemberNomination.objects.filter(
                category_nomination__event_category__category=category,
                member__event=self.id,
            )
            members = set(member_nominations.values_list("member", flat=True))
            top = []
            members_in_current_event = Member.objects.filter(event=self.id)
            for member in members:
                result_all = sum(
                    Result.objects.filter(
                        member_nomination__member=member,
                        member_nomination__category_nomination__event_category__category=category,
                    ).values_list("score", flat=True)
                )
                top.append(
                    {
                        "member": members_in_current_event.get(pk=member),
                        "result_all": result_all,
                    }
                )
            top = sorted(top, reverse=True, key=lambda x: x["result_all"])
            win_categories.append({"name": str(category), "members": top})
        return win_categories

    def __str__(self):
        return self.name


class Member(models.Model):
    user = models.ForeignKey(
        "users.User",
        models.PROTECT,
        help_text="Выберите пользователя",
        verbose_name="Пользователь",
    )
    event = models.ForeignKey(
        "Event",
        models.PROTECT,
        related_name="members",
        help_text="Выберите чемпионат",
        verbose_name="Чемпионат",
    )

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"

    def __str__(self) -> str:
        return f"Участник {self.user} --- {self.event}"


class EventCategory(models.Model):
    event = models.ForeignKey(
        "Event",
        models.PROTECT,
        help_text="Выберите чемпионат",
        verbose_name="Чемпионат",
    )
    category = models.ForeignKey(
        "Category",
        models.PROTECT,
        related_name="categories_in_EventCategoryModel",
        help_text="Выберите категорию",
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "Категории мероприятия"
        verbose_name_plural = "Категории мероприятий"

    def __str__(self) -> str:
        return f"{self.event} --- {self.category}"


class CategoryNomination(models.Model):
    event_category = models.ForeignKey(
        "EventCategory",
        models.PROTECT,
        default=None,
        null=True,
        help_text="Выберите категорию чемпионата",
        verbose_name="Категория чемпионата",
    )
    nomination = models.ForeignKey(
        "Nomination",
        models.PROTECT,
        related_name="nom",
        help_text="Выберите номинацию",
        verbose_name="Номинация",
    )
    event_staff = models.ManyToManyField(
        "users.User",
        blank=True,
        related_name="staffs",
        help_text="Выберите судей",
        verbose_name="Судьи",
    )

    class Meta:
        verbose_name = "Номинации категорий"
        verbose_name_plural = "Номинации категорий"

    def __str__(self) -> str:
        return f"{self.event_category} --- {self.nomination}"


class MemberNomination(models.Model):
    member = models.ForeignKey(
        "Member",
        models.PROTECT,
        related_name="membernom",
        help_text="Выберите участника",
        verbose_name="Участник",
    )
    category_nomination = models.ForeignKey(
        "CategoryNomination",
        models.PROTECT,
        related_name="categ",
        help_text="Выберите категорию номинацию",
        verbose_name="Категория номинации",
    )
    url_video = models.TextField(default="", blank=True)
    url_message_video = models.TextField(default="", blank=True)
    is_done = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.id:
            if self.category_nomination.event_staff.count() == self.results.count():
                self.is_done = True
            else:
                self.is_done = False
        super().save(*args, **kwargs)

    @property
    def result_sum(self):
        unique_results = self.results.order_by("event_staff").distinct("event_staff")

        return sum(result.score for result in unique_results)

    class Meta:
        verbose_name = "Номинация участника"
        verbose_name_plural = "Номинации участника"

    def __str__(self) -> str:
        return f"{self.member} --- {self.category_nomination}"


class MemberNominationPhoto(models.Model):
    BEFORE = "BE"
    AFTER = "AF"
    BEFORE_AFTER_CHOICES = [
        (BEFORE, "До"),
        (AFTER, "После"),
    ]

    member_nomination = models.ForeignKey(
        "MemberNomination",
        models.PROTECT,
        related_name="photos",
        default=None,
        help_text="Выберите работу участника",
        verbose_name="Работа участника",
    )
    photo = models.ImageField(
        storage=PrivateMediaStorage,
        upload_to="photos/%Y/%m/%d",
        help_text="Выберите фото работы",
        verbose_name="Фото работы",
    )
    optimized_photo = models.ImageField(
        storage=PrivateMediaStorage,
        default=None,
        blank=True,
        null=True,
        upload_to="optimized_photos/%Y/%m/%d",
        help_text="Поле заполняется автоматически",
        verbose_name="Оптимизированное фото. Трогать в крайнем случае.",
    )
    name = models.CharField(
        max_length=50,
        help_text="Введите название фотографии",
        verbose_name="Название фотографии",
    )
    before_after = models.CharField(
        max_length=2,
        choices=BEFORE_AFTER_CHOICES,
        help_text="Выберите статус фотографии",
        verbose_name="Статус фотографии",
    )

    def save(self, *args, **kwargs):
        if self.pk is None:
            # Количество фотографий в MemberNomination в момент сохранения новой фотографии
            photos_count_member_nomination = self.member_nomination.photos.count()

            # Количество фотографий в Nomination, относящейся к запрошенной MemberNomination
            photos_count_nomination = (
                self.member_nomination.category_nomination.nomination.get_photo_count()
            )

            if photos_count_member_nomination >= photos_count_nomination:
                return ValueError(
                    f"Максимум {photos_count_nomination} фотографии для данной MemberNomination."
                )

        # if self.optimized_photo.name is None or (
        #         self.optimized_photo.name is not None and
        #         splitext(basename(self.photo.name))[0] != splitext(basename(self.optimized_photo.name))[0]
        # ):
        #     # print(splitext(basename(self.photo.name))[0], splitext(basename(self.optimized_photo.name))[0])
        #     # print(basename(self.photo.name), basename(self.optimized_photo.name))
        #     optimize_image.delay(self.id)
        # else:
        #     print(splitext(basename(self.photo.name))[0], splitext(basename(self.optimized_photo.name))[0])
        #     print(basename(self.photo.name), basename(self.optimized_photo.name))

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Фотографии работы"
        verbose_name_plural = "Фотографии работ"

    def __str__(self) -> str:
        return f"{self.member_nomination}"


class Result(models.Model):
    member_nomination = models.ForeignKey(
        "MemberNomination",
        models.PROTECT,
        related_name="results",
        help_text="Выберите работу участника",
        verbose_name="Работа участника",
    )
    score = models.IntegerField(verbose_name="Баллы")
    event_staff = models.ForeignKey(
        "users.User", models.PROTECT, verbose_name="Судья, выдавший оценку"
    )
    score_retail = models.JSONField(
        default=None, null=True, verbose_name="Подробная оценка"
    )

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
        constraints = [
            constraints.UniqueConstraint(
                "member_nomination", "event_staff", name="unique_lower_name_category"
            )
        ]

    def __str__(self) -> str:
        return f"{self.score} --- {self.event_staff}"
