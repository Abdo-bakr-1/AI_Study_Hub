"""Tests for accounts app: registration, email verification, login, password reset."""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import EmailVerification, PasswordResetToken

User = get_user_model()


class RegisterViewTests(TestCase):
    """Tests for the registration flow."""

    @override_settings(EMAIL_VERIFICATION_REQUIRED=True)
    def test_register_creates_inactive_user(self):
        """New user is inactive before verification."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "testuser",
                "email": "test@example.com",
                "password1": "ComplexPass123",
                "password2": "ComplexPass123",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="testuser")
        self.assertFalse(user.is_active)

    @override_settings(EMAIL_VERIFICATION_REQUIRED=True)
    def test_register_creates_email_verification(self):
        """EmailVerification record is created on registration."""
        self.client.post(
            reverse("accounts:register"),
            {
                "username": "testuser2",
                "email": "test2@example.com",
                "password1": "ComplexPass123",
                "password2": "ComplexPass123",
            },
        )
        user = User.objects.get(username="testuser2")
        verifications = EmailVerification.objects.filter(user=user)
        self.assertEqual(verifications.count(), 1)
        verification = verifications.first()
        self.assertFalse(verification.is_verified)
        self.assertFalse(verification.is_expired)

    @override_settings(EMAIL_VERIFICATION_REQUIRED=True, BREVO_API_KEY="test-key")
    @patch("accounts.utils._send_via_brevo_api")
    def test_register_sends_verification_email(self, mock_brevo):
        """Verification email is sent via Brevo API with correct content."""
        mock_brevo.return_value = True
        self.client.post(
            reverse("accounts:register"),
            {
                "username": "testuser3",
                "email": "test3@example.com",
                "password1": "ComplexPass123",
                "password2": "ComplexPass123",
            },
        )
        self.assertTrue(mock_brevo.called)
        args = mock_brevo.call_args[0]
        # args = (subject, html_content, text_content, to_email, to_name)
        self.assertEqual(args[0], "Verify your AI Study Hub account")
        self.assertEqual(args[3], "test3@example.com")  # to_email
        self.assertEqual(args[4], "testuser3")  # to_name
        self.assertIn("verify-email", args[2])  # text_content

    @override_settings(EMAIL_VERIFICATION_REQUIRED=False)
    def test_register_no_verification_activates_user(self):
        """When verification is disabled, user is active immediately."""
        self.client.post(
            reverse("accounts:register"),
            {
                "username": "testuser4",
                "email": "test4@example.com",
                "password1": "ComplexPass123",
                "password2": "ComplexPass123",
            },
        )
        user = User.objects.get(username="testuser4")
        self.assertTrue(user.is_active)


class VerifyEmailViewTests(TestCase):
    """Tests for the email verification flow."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="verifyuser",
            email="verify@example.com",
            password="ComplexPass123",
            is_active=False,
        )
        self.verification = EmailVerification.objects.create(user=self.user)

    def test_valid_token_verifies_email(self):
        """Valid token verifies the email and activates the user."""
        response = self.client.get(
            reverse("accounts:verify_email", args=[self.verification.token])
        )
        self.assertEqual(response.status_code, 302)
        self.verification.refresh_from_db()
        self.assertTrue(self.verification.is_verified)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_invalid_token_rejected(self):
        """Invalid token is rejected with 404."""
        response = self.client.get(
            reverse("accounts:verify_email", args=["invalid-token-xyz"])
        )
        self.assertEqual(response.status_code, 404)

    def test_expired_token_rejected(self):
        """Expired token is rejected."""
        self.verification.expires_at = timezone.now() - timezone.timedelta(hours=1)
        self.verification.save()
        response = self.client.get(
            reverse("accounts:verify_email", args=[self.verification.token])
        )
        self.assertEqual(response.status_code, 302)
        self.verification.refresh_from_db()
        self.assertFalse(self.verification.is_verified)

    def test_used_token_cannot_be_reused(self):
        """Already verified token redirects with info message."""
        self.verification.is_verified = True
        self.verification.save()
        response = self.client.get(
            reverse("accounts:verify_email", args=[self.verification.token])
        )
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("already verified" in str(m) for m in messages))

    def test_verification_activates_correct_user_only(self):
        """Verification only activates the token's associated user."""
        other_user = User.objects.create_user(
            username="other", email="other@example.com", password="pass", is_active=False
        )
        response = self.client.get(
            reverse("accounts:verify_email", args=[self.verification.token])
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        other_user.refresh_from_db()
        self.assertFalse(other_user.is_active)


class LoginViewTests(TestCase):
    """Tests for login behavior with verification."""

    def setUp(self):
        self.inactive_user = User.objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password="ComplexPass123",
            is_active=False,
        )
        self.active_user = User.objects.create_user(
            username="active",
            email="active@example.com",
            password="ComplexPass123",
            is_active=True,
        )

    def test_login_before_verification_fails(self):
        """Login fails for inactive (unverified) user."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "inactive", "password": "ComplexPass123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_after_verification_succeeds(self):
        """Login succeeds for active (verified) user."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "active", "password": "ComplexPass123"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_shows_friendly_message_for_unverified(self):
        """Unverified user gets a helpful message."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "inactive", "password": "ComplexPass123"},
        )
        self.assertEqual(response.status_code, 200)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("not verified" in str(m) for m in messages))


class PasswordResetViewTests(TestCase):
    """Tests to ensure password reset still works after verification changes."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="OldPass123",
            is_active=True,
        )

    @override_settings(BREVO_API_KEY="test-key")
    @patch("accounts.utils._send_via_brevo_api")
    def test_password_reset_sends_email(self, mock_brevo):
        """Password reset request sends email."""
        mock_brevo.return_value = True
        response = self.client.post(
            reverse("accounts:password_reset_request"),
            {"email": "reset@example.com"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(mock_brevo.called)
        args = mock_brevo.call_args[0]
        self.assertEqual(args[0], "Reset your AI Study Hub password")

    @override_settings(BREVO_API_KEY="test-key")
    @patch("accounts.utils._send_via_brevo_api")
    def test_password_reset_confirm_works(self, mock_brevo):
        """Password reset confirmation works with valid token."""
        mock_brevo.return_value = True
        # Request reset
        self.client.post(
            reverse("accounts:password_reset_request"),
            {"email": "reset@example.com"},
        )
        token = PasswordResetToken.objects.filter(user=self.user).first()
        # Confirm reset
        response = self.client.post(
            reverse("accounts:password_reset_confirm", args=[token.token]),
            {"new_password1": "NewPass123", "new_password2": "NewPass123"},
        )
        self.assertEqual(response.status_code, 302)
        token.refresh_from_db()
        self.assertTrue(token.is_used)
        # Login with new password
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass123"))


class ResendVerificationTests(TestCase):
    """Tests for resend verification feature."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="resenduser",
            email="resend@example.com",
            password="ComplexPass123",
            is_active=False,
        )
        # Create an old pending verification record to pass the cooldown check.
        self.verification = EmailVerification.objects.create(user=self.user)
        self.verification.created_at = timezone.now() - timezone.timedelta(minutes=5)
        self.verification.save()

    @override_settings(BREVO_API_KEY="test-key")
    @patch("accounts.utils._send_via_brevo_api")
    def test_resend_verification_creates_new_token(self, mock_brevo):
        """Resend creates a new verification token."""
        mock_brevo.return_value = True
        response = self.client.post(
            reverse("accounts:resend_verification"),
            {"email": "resend@example.com"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(mock_brevo.called)
        verifications = EmailVerification.objects.filter(user=self.user)
        # Old one marked verified, new one created
        self.assertEqual(verifications.count(), 2)
        old = verifications.order_by("created_at").first()
        new = verifications.order_by("-created_at").first()
        self.assertTrue(old.is_verified)
        self.assertFalse(new.is_verified)

    @override_settings(BREVO_API_KEY="test-key")
    @patch("accounts.utils._send_via_brevo_api")
    def test_resend_verification_rate_limits(self, mock_brevo):
        """Resend rate limits (cooldown) prevents spam."""
        mock_brevo.return_value = True
        # First resend (old record passes cooldown)
        self.client.post(
            reverse("accounts:resend_verification"),
            {"email": "resend@example.com"},
        )
        self.assertEqual(mock_brevo.call_count, 1)
        # Immediate second resend (new token < 60s old) should be blocked
        response = self.client.post(
            reverse("accounts:resend_verification"),
            {"email": "resend@example.com"},
        )
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("wait a moment" in str(m) for m in messages))
        # Brevo should only be called once
        self.assertEqual(mock_brevo.call_count, 1)

    @override_settings(BREVO_API_KEY="test-key")
    @patch("accounts.utils._send_via_brevo_api")
    def test_resend_verification_does_not_leak_emails(self, mock_brevo):
        """Resend shows same message for existing and non-existing emails."""
        mock_brevo.return_value = True
        # Non-existing email
        response = self.client.post(
            reverse("accounts:resend_verification"),
            {"email": "nonexistent@example.com"},
        )
        # Brevo should NOT be called for non-existing email (no user)
        self.assertEqual(mock_brevo.call_count, 0)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any("If an account exists" in str(m) for m in messages)
        )


class BrevoAPIIntegrationTests(TestCase):
    """Tests for Brevo API email sending."""

    def _make_mock_response(self, status_code=201):
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.text = "OK" if status_code == 201 else "Error"
        return mock_resp

    @override_settings(BREVO_API_KEY="test-key", DEFAULT_FROM_EMAIL="AI Study Hub <no-reply@example.com>")
    @patch("accounts.utils.requests.post")
    def test_brevo_api_success(self, mock_post):
        """Successful Brevo API request returns True."""
        from accounts.utils import _send_via_brevo_api
        mock_post.return_value = self._make_mock_response(201)
        result = _send_via_brevo_api(
            "Test Subject",
            "<p>Test HTML</p>",
            "Test text content",
            "user@example.com",
            "testuser",
        )
        self.assertTrue(result)
        self.assertTrue(mock_post.called)
        # Verify correct endpoint and headers
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://api.brevo.com/v3/smtp/email")
        headers = kwargs["headers"]
        self.assertEqual(headers["api-key"], "test-key")
        self.assertEqual(headers["Content-Type"], "application/json")
        # Verify payload structure
        payload = kwargs["json"]
        self.assertEqual(payload["subject"], "Test Subject")
        self.assertEqual(payload["to"][0]["email"], "user@example.com")
        self.assertEqual(payload["sender"]["email"], "no-reply@example.com")

    @override_settings(BREVO_API_KEY="test-key")
    @patch("accounts.utils.requests.post")
    def test_brevo_api_failure(self, mock_post):
        """Brevo API error (non-201) returns False."""
        from accounts.utils import _send_via_brevo_api
        mock_post.return_value = self._make_mock_response(400)
        result = _send_via_brevo_api(
            "Test Subject",
            "<p>Test HTML</p>",
            "Test text content",
            "user@example.com",
            "testuser",
        )
        self.assertFalse(result)

    @override_settings(BREVO_API_KEY="")
    @patch("accounts.utils.requests.post")
    def test_brevo_api_no_key(self, mock_post):
        """Missing API key returns False without making request."""
        from accounts.utils import _send_via_brevo_api
        result = _send_via_brevo_api(
            "Test Subject",
            "<p>Test HTML</p>",
            "Test text content",
            "user@example.com",
            "testuser",
        )
        self.assertFalse(result)
        self.assertFalse(mock_post.called)

    @override_settings(BREVO_API_KEY="test-key")
    @patch("accounts.utils.requests.post")
    def test_brevo_api_timeout(self, mock_post):
        """Brevo API timeout returns False."""
        import requests
        from accounts.utils import _send_via_brevo_api
        mock_post.side_effect = requests.exceptions.Timeout()
        result = _send_via_brevo_api(
            "Test Subject",
            "<p>Test HTML</p>",
            "Test text content",
            "user@example.com",
            "testuser",
        )
        self.assertFalse(result)

    @override_settings(EMAIL_VERIFICATION_REQUIRED=True, BREVO_API_KEY="test-key")
    @patch("accounts.utils._send_via_brevo_api")
    def test_email_failure_keeps_user_inactive(self, mock_brevo):
        """When Brevo API fails, user remains inactive."""
        mock_brevo.return_value = False
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "brevofail",
                "email": "brevo@example.com",
                "password1": "ComplexPass123",
                "password2": "ComplexPass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="brevofail")
        self.assertFalse(user.is_active)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("couldn't send" in str(m) for m in messages))


class EmailVerificationModelTests(TestCase):
    """Tests for EmailVerification model properties."""

    def test_is_expired_property(self):
        """is_expired returns True when past expiry."""
        user = User.objects.create_user(
            username="modeltest", email="model@example.com", password="pass"
        )
        verification = EmailVerification.objects.create(user=user)
        verification.expires_at = timezone.now() - timezone.timedelta(hours=1)
        verification.save()
        self.assertTrue(verification.is_expired)

    def test_is_expired_false_when_valid(self):
        """is_expired returns False when not yet expired."""
        user = User.objects.create_user(
            username="modeltest2", email="model2@example.com", password="pass"
        )
        verification = EmailVerification.objects.create(user=user)
        self.assertFalse(verification.is_expired)