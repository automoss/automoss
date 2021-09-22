from django.contrib.auth.tokens import PasswordResetTokenGenerator

class ConfirmEmailTokenGenerator(PasswordResetTokenGenerator):
    """ Token generator for generating single-use, expiring tokens for email confirmation """
    def _make_hash_value(self, email, timestamp):
        """ Creates string to hash based on user state and info that changes """
        return f"{email.pk}{email.email}{timestamp}{email.is_verified}"

class UserTokenGenerator(PasswordResetTokenGenerator):
    """ Token generator for generating single-use, expiring tokens for password changing and account confirmation """
    def _make_hash_value(self, user, timestamp):
        """ Creates string to hash based on user state and info that changes """
        return f"{user.user_id}{user.course_code}{user.moss_id}{timestamp}{user.password}{user.is_verified}"

email_confirmation_token = ConfirmEmailTokenGenerator()
password_reset_token = UserTokenGenerator()
confirm_registration_token = UserTokenGenerator()