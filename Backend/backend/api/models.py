# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import datetime

class AuthUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(username, email, password, **extra_fields)

class AuthUser(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    email = models.CharField(max_length=254, blank=True, default='')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = AuthUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    class Meta:
        managed = False
        db_table = 'auth_user'

class Programme(models.Model):
    category = models.CharField(max_length=3, null=False, blank=False)
    name = models.CharField(max_length=70, null=False,unique=True, blank=False)
    programme_begin_year = models.PositiveIntegerField(default=datetime.date.today().year, null=False)

    class Meta:
        managed = False
        db_table = 'programme_curriculum_programme'

    def __str__(self):
        return str(self.category + " - " + self.name)
    
class Discipline(models.Model):
    name = models.CharField(max_length=100, null=False,unique=True, blank=False)
    acronym = models.CharField(max_length=10, null=False, default="", blank=False)
    programmes = models.ManyToManyField(Programme, blank=True)

    class Meta:
        managed = False
        db_table = 'programme_curriculum_discipline'

    def __str__(self):
        return str(self.name) + " " + str(self.acronym)


class Curriculum(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    version = models.DecimalField(default=1.0,max_digits=5,decimal_places=1)
    working_curriculum = models.BooleanField(default=True, null=False)
    no_of_semester = models.PositiveIntegerField(default=1, null=False)
    min_credit = models.PositiveIntegerField(default=0, null=False)
    latest_version = models.BooleanField(default=True)

    class Meta:
        unique_together = ('name', 'version',)
        managed = False
        db_table = 'programme_curriculum_curriculum'

    def __str__(self):
        return str(self.name + " v" + str(self.version))

class Batch(models.Model):

    name = models.CharField(max_length=50, null=False, blank=False)
    discipline = models.ForeignKey(Discipline, null=False, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(default=datetime.date.today().year, null=False)
    curriculum = models.ForeignKey(Curriculum, null=True, blank=True, on_delete=models.SET_NULL)
    running_batch = models.BooleanField(default=True)

    class Meta:
        unique_together = ('name', 'discipline', 'year',)
        managed = False
        db_table = 'programme_curriculum_batch'

    def __str__(self):
        return str(self.name) + " " + str(self.discipline.acronym) + " " + str(self.year)


class GlobalsDepartmentinfo(models.Model):
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'globals_departmentinfo'


class GlobalsDesignation(models.Model):
    name = models.CharField(unique=True, max_length=50)
    full_name = models.CharField(max_length=100)
    type = models.CharField(max_length=30)
    basic = models.BooleanField(default=False, null=False, blank=False)
    category = models.CharField(max_length=20, null=True, blank=True)
    dept_if_not_basic = models.ForeignKey(GlobalsDepartmentinfo, on_delete=models.CASCADE, blank=True, null=True)
    is_singular = models.BooleanField(default=False, help_text="If True, only one user can hold this role at a time")
    
    class Meta:
        managed = False
        db_table = 'globals_designation'


class GlobalsExtrainfo(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    title = models.CharField(max_length=20)
    sex = models.CharField(max_length=2)
    date_of_birth = models.DateField()
    user_status = models.CharField(max_length=50)
    address = models.TextField()
    phone_no = models.BigIntegerField(blank=True, null=True)
    user_type = models.CharField(max_length=20)
    profile_picture = models.CharField(max_length=100, blank=True, null=True)
    about_me = models.TextField()
    date_modified = models.DateTimeField(blank=True, null=True)
    department = models.ForeignKey(GlobalsDepartmentinfo, on_delete=models.CASCADE, blank=True, null=True)
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'globals_extrainfo'

class Staff(models.Model):
    id = models.OneToOneField(GlobalsExtrainfo, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        managed = False
        db_table = 'globals_staff'


class GlobalsHoldsdesignation(models.Model):
    held_at = models.DateTimeField(auto_now=True)
    start_date = models.DateField(null=True, blank=True, help_text="Role assignment start date (optional)")
    end_date = models.DateField(null=True, blank=True, help_text="Role assignment end date (optional)")
    designation = models.ForeignKey(GlobalsDesignation, related_name='designees', on_delete=models.CASCADE)
    user = models.ForeignKey(AuthUser, related_name='holds_designations', on_delete=models.CASCADE)
    working = models.ForeignKey(AuthUser, related_name='current_designation', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'globals_holdsdesignation'
        unique_together = (('user', 'designation'), ('working', 'designation'),)


class GlobalsModuleaccess(models.Model):
    designation = models.CharField(max_length=155)
    program_and_curriculum = models.BooleanField()
    course_registration = models.BooleanField()
    course_management = models.BooleanField()
    other_academics = models.BooleanField()
    spacs = models.BooleanField()
    department = models.BooleanField()
    examinations = models.BooleanField()
    hr = models.BooleanField()
    iwd = models.BooleanField()
    complaint_management = models.BooleanField()
    fts = models.BooleanField()
    purchase_and_store = models.BooleanField()
    rspc = models.BooleanField()
    hostel_management = models.BooleanField()
    mess_management = models.BooleanField()
    gymkhana = models.BooleanField()
    placement_cell = models.BooleanField()
    visitor_hostel = models.BooleanField()
    phc = models.BooleanField()
    inventory_management = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'globals_moduleaccess'

class Student(models.Model):

    id = models.OneToOneField(GlobalsExtrainfo, on_delete=models.CASCADE, primary_key=True)
    programme = models.CharField(max_length=10)
    batch = models.IntegerField(default=2016)
    batch_id = models.ForeignKey(Batch, null=True, blank=True, on_delete=models.CASCADE)
    cpi = models.FloatField(default=0)
    category = models.CharField(max_length=10, null=False)
    father_name = models.CharField(max_length=40, default='',null=True)
    mother_name = models.CharField(max_length=40, default='',null=True)
    hall_no = models.IntegerField(default=0)
    room_no = models.CharField(max_length=10, blank=True, null=True)
    specialization = models.CharField(max_length=40, null=True, default='')
    curr_semester_no = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'academic_information_student'

    def __str__(self):
        username = str(self.id.user.username)
        return username
    
    
class GlobalsFaculty(models.Model):

    id = models.OneToOneField(GlobalsExtrainfo, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        managed = False
        db_table = 'globals_faculty'


class AuditLog(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(AuthUser, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)  # e.g., 'CREATE_USER', 'UPDATE_ROLE', 'ARCHIVE_USER'
    model_name = models.CharField(max_length=100, blank=True, null=True)  # e.g., 'AuthUser', 'GlobalsDesignation'
    object_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)  # Track browser/client
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='SUCCESS')  # 'SUCCESS' or 'FAILED'

    class Meta:
        managed = True
        db_table = 'audit_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['status', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.timestamp} - {self.user.username if self.user else 'Unknown'} - {self.action}"