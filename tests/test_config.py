"""Tests for configuration loading and validation."""

import pytest
from pydantic import ValidationError

from tick_task.config import Settings, settings


class TestSettingsValidation:
    """Test cases for settings validation."""

    def test_settings_creation_default(self):
        """Test creating settings with defaults."""
        test_settings = Settings()

        # Check that required fields have defaults
        assert test_settings.database_url is not None
        assert "sqlite" in test_settings.database_url

    def test_settings_database_url_validation(self):
        """Test database URL validation."""
        # Valid SQLite URL
        settings = Settings(database_url="sqlite:///test.db")
        assert settings.database_url == "sqlite:///test.db"

        # Valid async SQLite URL
        settings = Settings(database_url="sqlite+aiosqlite:///test.db")
        assert settings.database_url == "sqlite+aiosqlite:///test.db"

    def test_settings_custom_values(self):
        """Test settings with custom values."""
        settings = Settings(
            database_url="sqlite:///custom.db",
            debug=True,
        )

        assert settings.database_url == "sqlite:///custom.db"
        assert settings.debug is True


class TestGlobalSettings:
    """Test cases for the global settings instance."""

    def test_global_settings_is_settings_instance(self):
        """Test that the global settings is a Settings instance."""
        assert isinstance(settings, Settings)

    def test_global_settings_has_database_url(self):
        """Test that global settings has a database URL."""
        assert hasattr(settings, "database_url")
        assert settings.database_url is not None

    def test_global_settings_database_url_is_sqlite(self):
        """Test that global settings uses SQLite."""
        assert "sqlite" in settings.database_url
