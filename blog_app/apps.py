from django.apps import AppConfig


class BlogAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # 64 bit
    name = 'blog_app'

    def ready(self):
        # импортировать обработчики сигналов
        # noinspection PyUnresolvedReferences
        import blog_app.signals
