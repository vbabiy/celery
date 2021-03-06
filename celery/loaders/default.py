from celery.loaders.base import BaseLoader

DEFAULT_SETTINGS = {
    "DEBUG": False,
    "DATABASE_ENGINE": "sqlite3",
    "DATABASE_NAME": "celery.sqlite",
    "INSTALLED_APPS": ("celery", ),
}


def wanted_module_item(item):
    is_private = item.startswith("_")
    return not is_private


class Loader(BaseLoader):
    """The default loader.

    See the FAQ for example usage.

    """

    def read_configuration(self):
        """Read configuration from ``celeryconf.py`` and configure
        celery and Django so it can be used by regular Python."""
        config = dict(DEFAULT_SETTINGS)
        import celeryconfig
        usercfg = dict((key, getattr(celeryconfig, key))
                            for key in dir(celeryconfig)
                                if wanted_module_item(key))
        config.update(usercfg)
        from django.conf import settings
        if not settings.configured:
            settings.configure()
        for config_key, config_value in usercfg.items():
            setattr(settings, config_key, config_value)
        return settings

    def on_worker_init(self):
        """Imports modules at worker init so tasks can be registered
        and used by the worked.

        The list of modules to import is taken from the ``CELERY_IMPORTS``
        setting in ``celeryconf.py``.

        """
        imports = getattr(self.conf, "CELERY_IMPORTS", [])
        for module in imports:
            __import__(module, [], [], [''])
