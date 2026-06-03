import re
import unicodedata
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def contains_cjk(value):
    """Check if string contains Japanese, Chinese, Korean characters"""
    for char in value:
        if unicodedata.category(char) in ("Lo",) and ord(char) > 0x2E7F:
            return True
    return False


def contains_emoji(value):
    """Check if string contains emoji"""
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"
        "\U0001f300-\U0001f5ff"
        "\U0001f680-\U0001f6ff"
        "\U0001f1e0-\U0001f1ff"
        "\U00002702-\U000027b0"
        "\U000024c2-\U0001f251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2b55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"
        "\u3030"
        "]+",
        flags=re.UNICODE,
    )
    return bool(emoji_pattern.search(value))


def contains_sql_injection(value):
    """Check for common SQL injection patterns"""
    sql_patterns = [
        r"(\s|^)(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|TRUNCATE)(\s|$)",
        r"--",
        r";",
        r"\/\*.*\*\/",
        r"xp_",
        r"CAST\s*\(",
        r"CONVERT\s*\(",
    ]
    value_upper = value.upper()
    for pattern in sql_patterns:
        if re.search(pattern, value_upper):
            return True
    return False


def contains_xss(value):
    """Check for common XSS patterns"""
    xss_patterns = [
        r"<script",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<img.*onerror",
        r"eval\s*\(",
        r"document\.cookie",
        r"window\.location",
        r"<svg.*onload",
    ]
    value_lower = value.lower()
    for pattern in xss_patterns:
        if re.search(pattern, value_lower):
            return True
    return False


def validate_name(value):
    """
    Name validator — allows:
    - Latin characters (English)
    - CJK characters (Chinese, Japanese, Korean)
    - Arabic, Thai, and other Unicode letters
    - Spaces, hyphens, apostrophes
    Blocks:
    - Emojis
    - Numbers
    - Special characters except - and '
    - SQL injection / XSS
    """
    if not value or not value.strip():
        raise ValidationError(_("Name cannot be empty or just spaces."))

    if len(value.strip()) < 2:
        raise ValidationError(_("Name must be at least 2 characters."))

    if len(value) > 100:
        raise ValidationError(_("Name cannot exceed 100 characters."))

    if contains_emoji(value):
        raise ValidationError(_("Name cannot contain emojis."))

    if contains_sql_injection(value):
        raise ValidationError(_("Name contains invalid characters."))

    if contains_xss(value):
        raise ValidationError(_("Name contains invalid characters."))

    allowed_pattern = re.compile(r"^[\w\s\-']+$", re.UNICODE)
    if not allowed_pattern.match(value):
        raise ValidationError(
            _("Name can only contain letters, spaces, hyphens, and apostrophes.")
        )

    return value


def validate_username(value):
    """
    Username validator:
    - Only ASCII letters, numbers, underscores, hyphens
    - No spaces
    - No CJK, no emoji
    - No SQL/XSS
    - 3-30 characters
    """
    if not value or not value.strip():
        raise ValidationError(_("Username cannot be empty."))

    value = value.strip()

    if len(value) < 3:
        raise ValidationError(_("Username must be at least 3 characters."))

    if len(value) > 30:
        raise ValidationError(_("Username cannot exceed 30 characters."))

    if " " in value:
        raise ValidationError(_("Username cannot contain spaces."))

    if contains_emoji(value):
        raise ValidationError(_("Username cannot contain emojis."))

    if contains_cjk(value):
        raise ValidationError(
            _(
                "Username can only contain English letters, numbers, underscores, and hyphens."
            )
        )

    if contains_sql_injection(value):
        raise ValidationError(_("Username contains invalid characters."))

    if contains_xss(value):
        raise ValidationError(_("Username contains invalid characters."))

    if not re.match(r"^[a-zA-Z0-9_-]+$", value):
        raise ValidationError(
            _(
                "Username can only contain English letters, numbers, underscores (_), and hyphens (-)."
            )
        )

    if value[0] in "-_" or value[-1] in "-_":
        raise ValidationError(
            _("Username cannot start or end with a hyphen or underscore.")
        )

    return value


def validate_email_field(value):
    """
    Email validator:
    - Standard email format
    - No CJK characters
    - No emoji
    - No SQL/XSS
    - Max 254 characters (RFC standard)
    - Blocked disposable email domains
    """
    if not value or not value.strip():
        raise ValidationError(_("Email cannot be empty."))

    value = value.lower().strip()

    if len(value) > 254:
        raise ValidationError(_("Email cannot exceed 254 characters."))

    if contains_emoji(value):
        raise ValidationError(_("Email cannot contain emojis."))

    if contains_cjk(value):
        raise ValidationError(_("Email must use standard ASCII characters only."))

    if contains_sql_injection(value):
        raise ValidationError(_("Email contains invalid characters."))

    if contains_xss(value):
        raise ValidationError(_("Email contains invalid characters."))

    email_regex = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
    if not email_regex.match(value):
        raise ValidationError(_("Enter a valid email address (e.g. john@example.com)."))

    blocked_domains = [
        "mailinator.com",
        "guerrillamail.com",
        "tempmail.com",
        "throwam.com",
        "sharklasers.com",
        "yopmail.com",
        "10minutemail.com",
        "trashmail.com",
        "fakeinbox.com",
        "maildrop.cc",
        "dispostable.com",
    ]
    domain = value.split("@")[1]
    if domain in blocked_domains:
        raise ValidationError(
            _("Please use a valid business or personal email address.")
        )

    return value


def validate_password_field(value):
    """
    Password validator:
    - Min 8 characters
    - Max 128 characters
    - Must have uppercase
    - Must have lowercase
    - Must have number
    - Must have special character
    - No spaces
    - No CJK characters
    - No emoji
    """
    if not value:
        raise ValidationError(_("Password cannot be empty."))

    if len(value) < 8:
        raise ValidationError(_("Password must be at least 8 characters long."))

    if len(value) > 128:
        raise ValidationError(_("Password cannot exceed 128 characters."))

    if " " in value:
        raise ValidationError(_("Password cannot contain spaces."))

    if contains_emoji(value):
        raise ValidationError(_("Password cannot contain emojis."))

    if contains_cjk(value):
        raise ValidationError(_("Password can only contain ASCII characters."))

    if not re.search(r"[A-Z]", value):
        raise ValidationError(
            _("Password must contain at least one uppercase letter (A-Z).")
        )

    if not re.search(r"[a-z]", value):
        raise ValidationError(
            _("Password must contain at least one lowercase letter (a-z).")
        )

    if not re.search(r"\d", value):
        raise ValidationError(_("Password must contain at least one number (0-9)."))

    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-\[\]\\\/`~\';+=]', value):
        raise ValidationError(
            _("Password must contain at least one special character (!@#$%^&* etc).")
        )

    common_passwords = [
        "password",
        "password123",
        "12345678",
        "qwerty123",
        "admin123",
        "letmein1",
        "welcome1",
        "monkey123",
        "nautcore",
        "nauticore",
        "nauticore123",
    ]
    if value.lower() in common_passwords:
        raise ValidationError(
            _("This password is too common. Please choose a stronger password.")
        )

    return value


def validate_phone(value):
    """
    Phone validator:
    - Only numbers, +, -, spaces, parentheses
    - Min 7, max 20 characters
    - No letters, no emoji, no CJK
    """
    if not value:
        return value

    if contains_emoji(value):
        raise ValidationError(_("Phone number cannot contain emojis."))

    if len(value) < 7:
        raise ValidationError(_("Phone number is too short."))

    if len(value) > 20:
        raise ValidationError(_("Phone number cannot exceed 20 characters."))

    if not re.match(r"^[\d\+\-\s\(\)]+$", value):
        raise ValidationError(
            _("Phone number can only contain digits, +, -, spaces, and parentheses.")
        )

    return value


def validate_no_emoji(value):
    """Generic no-emoji validator for any text field"""
    if contains_emoji(value):
        raise ValidationError(_("This field cannot contain emojis."))
    return value


def validate_no_sql_xss(value):
    """Generic security validator for any text field"""
    if contains_sql_injection(value):
        raise ValidationError(_("Input contains invalid characters."))
    if contains_xss(value):
        raise ValidationError(_("Input contains invalid characters."))
    return value


def validate_text_field(value, max_length=500, allow_cjk=True):
    """
    Generic text field validator
    - Blocks emoji, SQL, XSS
    - Optional CJK support
    - Configurable max length
    """
    if not value:
        return value

    if contains_emoji(value):
        raise ValidationError(_("This field cannot contain emojis."))

    if not allow_cjk and contains_cjk(value):
        raise ValidationError(_("This field only supports standard ASCII characters."))

    if contains_sql_injection(value):
        raise ValidationError(_("Input contains invalid characters."))

    if contains_xss(value):
        raise ValidationError(_("Input contains invalid characters."))

    if len(value) > max_length:
        raise ValidationError(_(f"This field cannot exceed {max_length} characters."))

    return value
