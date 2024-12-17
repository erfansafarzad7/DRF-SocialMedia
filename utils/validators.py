from django.core.validators import RegexValidator


# Validator for Iranian mobile numbers (starts with 09 and followed by 9 digits)
phone_regex = RegexValidator(
    regex=r'^09\d{9}$',
    message="Mobile Number Must Be Like: 09123456789"
)
