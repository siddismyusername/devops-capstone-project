"""Regression tests for environment-driven service configuration."""
import os
import runpy
from unittest import TestCase
from unittest.mock import patch

from service import config


class TestConfiguration(TestCase):
    """Ensure database configuration respects explicit and fallback settings."""

    def test_build_database_uri_from_environment(self):
        """Build the Postgres URL when DATABASE_URI is not supplied."""
        values = {
            "DATABASE_URI": "",
            "DATABASE_USER": "coverage_user",
            "DATABASE_PASSWORD": "coverage_password",
            "DATABASE_NAME": "coverage_db",
            "DATABASE_HOST": "db.example",
        }
        with patch.dict(os.environ, values):
            settings = runpy.run_path(config.__file__)

        self.assertEqual(
            settings["SQLALCHEMY_DATABASE_URI"],
            "postgresql://coverage_user:coverage_password@db.example:5432/coverage_db",
        )
        self.assertFalse(settings["SQLALCHEMY_TRACK_MODIFICATIONS"])

    def test_explicit_database_uri_takes_precedence(self):
        """An explicit DATABASE_URI should not be replaced by fallback values."""
        with patch.dict(
            os.environ,
            {"DATABASE_URI": "sqlite:///explicit.db", "SECRET_KEY": "test-secret"},
        ):
            settings = runpy.run_path(config.__file__)

        self.assertEqual(settings["SQLALCHEMY_DATABASE_URI"], "sqlite:///explicit.db")
        self.assertEqual(settings["SECRET_KEY"], "test-secret")
