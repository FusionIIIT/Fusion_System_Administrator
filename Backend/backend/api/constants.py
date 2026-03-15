"""
Constants for System Administrator Module

Centralized location for all constants, choices, and default values.
Uses Django TextChoices for better type safety and maintainability.
"""

from django.db import models


class GenderChoices(models.TextChoices):
    """Gender options"""
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    OTHER = 'O', 'Other'


class UserStatusChoices(models.TextChoices):
    """User status options"""
    PRESENT = 'PRESENT', 'Present'
    ABSENT = 'ABSENT', 'Absent'
    SUSPENDED = 'SUSPENDED', 'Suspended'
    EXPELLED = 'EXPELLED', 'Expelled'
    GRADUATED = 'GRADUATED', 'Graduated'
    LEFT = 'LEFT', 'Left'


class UserTypeChoices(models.TextChoices):
    """User type options"""
    STUDENT = 'student', 'Student'
    FACULTY = 'faculty', 'Faculty'
    STAFF = 'staff', 'Staff'


class CategoryChoices(models.TextChoices):
    """Reservation category options"""
    GEN = 'GEN', 'General'
    OBC = 'OBC', 'OBC'
    SC = 'SC', 'SC'
    ST = 'ST', 'ST'
    EWS = 'EWS', 'EWS'


class ProgrammeChoices(models.TextChoices):
    """Programme options"""
    BTECH = 'B.Tech', 'Bachelor of Technology'
    MTECH = 'M.Tech', 'Master of Technology'
    PHD = 'PhD', 'Doctor of Philosophy'
    MBA = 'MBA', 'Master of Business Administration'
    MDES = 'M.Des', 'Master of Design'
    MSC = 'M.Sc', 'Master of Science'
    PGDIPLoma = 'PG Diploma', 'Post Graduate Diploma'


class DesignationCategoryChoices(models.TextChoices):
    """Designation category options"""
    STUDENT = 'student', 'Student'
    FACULTY = 'faculty', 'Faculty'
    STAFF = 'staff', 'Staff'
    MANAGEMENT = 'management', 'Management'
    OTHER = 'other', 'Other'


# Default Values
DEFAULT_VALUES = {
    # User defaults
    'DEFAULT_IS_STAFF': False,
    'DEFAULT_IS_SUPERUSER': False,
    'DEFAULT_IS_ACTIVE': True,
    'DEFAULT_PASSWORD': 'user@123',
    
    # Extra info defaults
    'DEFAULT_TITLE_MALE': 'Mr.',
    'DEFAULT_TITLE_FEMALE': 'Ms.',
    'DEFAULT_DATE_OF_BIRTH': '2025-01-01',
    'DEFAULT_USER_STATUS': UserStatusChoices.PRESENT,
    'DEFAULT_ADDRESS': 'NA',
    'DEFAULT_PHONE_NO': 9999999999,
    'DEFAULT_ABOUT_ME': 'NA',
    'DEFAULT_DEPARTMENT': 'CSE',
    
    # Student defaults
    'DEFAULT_PROGRAMME': ProgrammeChoices.BTECH,
    'DEFAULT_BATCH_YEAR': None,  # Will be set to current year
    'DEFAULT_CPI': 0.0,
    'DEFAULT_CATEGORY': CategoryChoices.GEN,
    'DEFAULT_HALL_NO': 3,
    'DEFAULT_SEMESTER': None,  # Will be calculated
    
    # Module access defaults (all False)
    'DEFAULT_MODULE_ACCESS': {
        'program_and_curriculum': False,
        'course_registration': False,
        'course_management': False,
        'other_academics': False,
        'spacs': False,
        'department': False,
        'examinations': False,
        'hr': False,
        'iwd': False,
        'complaint_management': False,
        'fts': False,
        'purchase_and_store': False,
        'rspc': False,
        'hostel_management': False,
        'mess_management': False,
        'gymkhana': False,
        'placement_cell': False,
        'visitor_hostel': False,
        'phc': False,
        'inventory_management': False,
    }
}

# Email Configuration
EMAIL_CONFIG = {
    'SUBJECT_PASSWORD_RESET': 'Your Password has been reset!!',
    'SUBJECT_WELCOME': 'Welcome to Fusion Portal',
    'SUBJECT_CREDENTIALS': 'Fusion Portal Credentials',
    'PORTAL_URLS': [
        'http://fusion.iiitdmj.ac.in:8000',
        'http://fusion.iiitdmj.ac.in/',
        'http://172.27.16.216:8000/',
    ],
}

# Validation Rules
VALIDATION_RULES = {
    'USERNAME_MIN_LENGTH': 3,
    'USERNAME_MAX_LENGTH': 150,
    'PASSWORD_MIN_LENGTH': 8,
    'FIRST_NAME_MAX_LENGTH': 150,
    'LAST_NAME_MAX_LENGTH': 150,
    'EMAIL_MAX_LENGTH': 254,
}

# File Upload Configuration
FILE_UPLOAD_CONFIG = {
    'ALLOWED_EXTENSIONS': ['csv'],
    'MAX_FILE_SIZE_MB': 10,
    'CSV_HEADERS_REQUIRED': [
        'username',
        'first_name',
        'last_name',
        'sex',
        'category',
        'father_name',
        'mother_name',
        'batch',
        'programme',
        'title',
        'dob',
        'address',
        'phone_no',
        'department',
    ],
}

# API Response Messages
RESPONSE_MESSAGES = {
    'SUCCESS': {
        'USER_CREATED': 'User created successfully',
        'USER_UPDATED': 'User updated successfully',
        'ROLE_ASSIGNED': 'Role assigned successfully',
        'ROLES_UPDATED': 'User roles updated successfully',
        'DESIGNATION_CREATED': 'Designation created successfully',
        'MODULE_ACCESS_CREATED': 'Module access created successfully',
        'MAIL_SENT': 'Email sent successfully',
        'PASSWORD_RESET': 'Password reset successfully',
    },
    'ERROR': {
        'USER_NOT_FOUND': 'User not found',
        'DESIGNATION_NOT_FOUND': 'Designation not found',
        'MODULE_ACCESS_NOT_FOUND': 'Module access not found',
        'INVALID_DATA': 'Invalid data provided',
        'MISSING_FIELDS': 'Missing required fields',
        'DUPLICATE_USER': 'User with this username already exists',
        'CREATION_FAILED': 'Failed to create record',
        'UPDATE_FAILED': 'Failed to update record',
        'MAIL_SEND_FAILED': 'Failed to send email',
    },
    'INFO': {
        'NO_ROLES_FOUND': 'User has no designations',
        'NO_MODULES_FOUND': 'No module access configured',
    }
}

# Helper Functions
def get_default_title(gender):
    """Get default title based on gender"""
    if gender and gender[0].upper() == 'F':
        return DEFAULT_VALUES['DEFAULT_TITLE_FEMALE']
    return DEFAULT_VALUES['DEFAULT_TITLE_MALE']


def calculate_semester(batch_year):
    """Calculate current semester based on batch year"""
    from datetime import datetime
    now = datetime.now()
    return 2 * (now.year - int(batch_year)) + now.month // 7


def format_email(username):
    """Format email address for user"""
    return f"{username.lower()}@iiitdmj.ac.in"
