"""Security tests for Django settings configuration."""

from django.conf import settings


class TestSecuritySettings:
    """Tests that security settings are properly configured."""

    def test_session_cookie_httponly(self):
        """Test that session cookie has HttpOnly flag."""
        assert settings.SESSION_COOKIE_HTTPONLY is True

    def test_session_cookie_samesite(self):
        """Test that session cookie has SameSite attribute."""
        assert settings.SESSION_COOKIE_SAMESITE == "Lax"

    def test_content_type_nosniff(self):
        """Test that Content-Type sniffing is disabled."""
        assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True

    def test_x_frame_options(self):
        """Test that clickjacking protection is enabled."""
        assert settings.X_FRAME_OPTIONS == "DENY"


class TestAllowedHostsDev:
    """Tests for ALLOWED_HOSTS in development settings."""

    def test_allowed_hosts_not_wildcard(self):
        """Test that ALLOWED_HOSTS doesn't allow all hosts in dev."""
        # In dev settings, we should have restricted hosts
        from config.settings import dev

        assert dev.ALLOWED_HOSTS != ["*"]
        assert "*" not in dev.ALLOWED_HOSTS

    def test_allowed_hosts_includes_localhost(self):
        """Test that localhost is in ALLOWED_HOSTS."""
        from config.settings import dev

        assert "localhost" in dev.ALLOWED_HOSTS or "127.0.0.1" in dev.ALLOWED_HOSTS


class TestDatabase:
    """Tests for database configuration."""

    def test_database_is_sqlite(self):
        """Test that database engine is SQLite."""
        assert "sqlite3" in settings.DATABASES["default"]["ENGINE"]


class TestMiddleware:
    """Tests that security middleware is properly configured."""

    def test_security_middleware_present(self):
        """Test that SecurityMiddleware is in MIDDLEWARE."""
        assert "django.middleware.security.SecurityMiddleware" in settings.MIDDLEWARE

    def test_csrf_middleware_present(self):
        """Test that CsrfViewMiddleware is in MIDDLEWARE."""
        assert "django.middleware.csrf.CsrfViewMiddleware" in settings.MIDDLEWARE

    def test_clickjacking_middleware_present(self):
        """Test that XFrameOptionsMiddleware is in MIDDLEWARE."""
        assert (
            "django.middleware.clickjacking.XFrameOptionsMiddleware"
            in settings.MIDDLEWARE
        )


class TestPasswordValidators:
    """Tests that password validators are configured."""

    def test_password_validators_configured(self):
        """Test that password validators are set."""
        assert len(settings.AUTH_PASSWORD_VALIDATORS) > 0

    def test_minimum_length_validator_present(self):
        """Test that minimum length validator is present."""
        validator_names = [v["NAME"] for v in settings.AUTH_PASSWORD_VALIDATORS]
        assert any("MinimumLengthValidator" in name for name in validator_names)

    def test_common_password_validator_present(self):
        """Test that common password validator is present."""
        validator_names = [v["NAME"] for v in settings.AUTH_PASSWORD_VALIDATORS]
        assert any("CommonPasswordValidator" in name for name in validator_names)
