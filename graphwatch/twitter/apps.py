from django.apps import AppConfig


class TwitterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "graphwatch.twitter"

    def ready(self):
        try:
            import graphwatch.twitter.signals  # noqa F401
        except ImportError:
            pass
