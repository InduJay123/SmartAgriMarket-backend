"""
App configuration for ML API.
"""

from django.apps import AppConfig


class MlApiConfig(AppConfig):
    """Configuration class for ML API app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ml_api'
    verbose_name = 'Machine Learning API'

    def ready(self):
        """Initialize the app."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("ML API app is ready")
