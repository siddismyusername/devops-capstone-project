"""Regression tests for uncovered application error and logging paths."""
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch

from service import app
from service.common.error_handlers import internal_server_error
from service.common.log_handlers import init_logging
from service.common import status


class TestErrorAndLoggingCoverage(TestCase):
    """Exercise production branches previously missing from coverage."""

    def test_internal_error_returns_json_and_500(self):
        """The registered server-error handler returns a structured response."""
        with app.app_context():
            response, http_status = internal_server_error(
                RuntimeError("Simulated server error")
            )

        self.assertEqual(http_status, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.get_json()["error"], "Internal Server Error")
        self.assertEqual(response.get_json()["status"], 500)

    def test_existing_log_handlers_receive_formatter(self):
        """Gunicorn's existing handlers receive the application formatter."""
        handler = MagicMock()
        source_logger = MagicMock()
        source_logger.handlers = [handler]
        source_logger.level = logging.WARNING
        application = MagicMock()

        with patch(
            "service.common.log_handlers.logging.getLogger",
            return_value=source_logger,
        ) as get_logger:
            init_logging(application, "gunicorn.error")

        get_logger.assert_called_once_with("gunicorn.error")
        self.assertIs(application.logger.handlers, source_logger.handlers)
        application.logger.setLevel.assert_called_once_with(logging.WARNING)
        handler.setFormatter.assert_called_once()
        self.assertIsInstance(
            handler.setFormatter.call_args.args[0], logging.Formatter
        )
