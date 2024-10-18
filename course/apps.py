from django.apps import AppConfig


class CourseConfig(AppConfig):
    name = "course"

    def ready(self) -> None:
        # from django.db.models.signals import post_save
        # from .models import CourseAllocation
        # from .signals import create_course_allocation

        # post_save.connect(create_course_allocation, sender=CourseAllocation)

        return super().ready()