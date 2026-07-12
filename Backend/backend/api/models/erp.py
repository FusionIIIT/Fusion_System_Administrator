import datetime

from django.db import models


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "auth_user"


class Programme(models.Model):
    category = models.CharField(max_length=3, null=False, blank=False)
    name = models.CharField(max_length=70, null=False, unique=True, blank=False)
    programme_begin_year = models.PositiveIntegerField(
        default=datetime.date.today().year, null=False
    )

    class Meta:
        managed = False
        db_table = "programme_curriculum_programme"

    def __str__(self):
        return str(self.category + " - " + self.name)


class Discipline(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True, blank=False)
    acronym = models.CharField(max_length=10, null=False, default="", blank=False)
    programmes = models.ManyToManyField(Programme, blank=True)

    class Meta:
        managed = False
        db_table = "programme_curriculum_discipline"

    def __str__(self):
        return str(self.name) + " " + str(self.acronym)


class Curriculum(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    version = models.DecimalField(default=1.0, max_digits=5, decimal_places=1)
    working_curriculum = models.BooleanField(default=True, null=False)
    no_of_semester = models.PositiveIntegerField(default=1, null=False)
    min_credit = models.PositiveIntegerField(default=0, null=False)
    latest_version = models.BooleanField(default=True)

    class Meta:
        unique_together = (
            "name",
            "version",
        )
        managed = False
        db_table = "programme_curriculum_curriculum"

    def __str__(self):
        return str(self.name + " v" + str(self.version))


class Batch(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    discipline = models.ForeignKey(Discipline, null=False, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(default=datetime.date.today().year, null=False)
    curriculum = models.ForeignKey(
        Curriculum, null=True, blank=True, on_delete=models.SET_NULL
    )
    running_batch = models.BooleanField(default=True)
    total_seats = models.IntegerField(default=0)
    curriculum_options = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = (
            "name",
            "discipline",
            "year",
        )
        managed = False
        db_table = "programme_curriculum_batch"

    def __str__(self):
        return (
            str(self.name) + " " + str(self.discipline.acronym) + " " + str(self.year)
        )


class GlobalsDepartmentinfo(models.Model):
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = "globals_departmentinfo"


class GlobalsDesignation(models.Model):
    name = models.CharField(unique=True, max_length=50)
    full_name = models.CharField(max_length=100)
    type = models.CharField(max_length=30)
    basic = models.BooleanField(default=False, null=False, blank=False)
    category = models.CharField(max_length=20, null=True, blank=True)
    dept_if_not_basic = models.ForeignKey(
        GlobalsDepartmentinfo, on_delete=models.CASCADE, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "globals_designation"


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
    department = models.ForeignKey(
        GlobalsDepartmentinfo, on_delete=models.CASCADE, blank=True, null=True
    )
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "globals_extrainfo"


class Staff(models.Model):
    id = models.OneToOneField(
        GlobalsExtrainfo, on_delete=models.CASCADE, primary_key=True
    )

    def __str__(self):
        return str(self.id)

    class Meta:
        managed = False
        db_table = "globals_staff"


class GlobalsHoldsdesignation(models.Model):
    held_at = models.DateTimeField(auto_now=True)
    designation = models.ForeignKey(
        GlobalsDesignation, related_name="designees", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        AuthUser, related_name="holds_designations", on_delete=models.CASCADE
    )
    working = models.ForeignKey(
        AuthUser, related_name="current_designation", on_delete=models.CASCADE
    )

    class Meta:
        managed = False
        db_table = "globals_holdsdesignation"
        unique_together = (
            ("user", "designation"),
            ("working", "designation"),
        )


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
        db_table = "globals_moduleaccess"


class Student(models.Model):
    id = models.OneToOneField(
        GlobalsExtrainfo, on_delete=models.CASCADE, primary_key=True
    )
    programme = models.CharField(max_length=10)
    batch = models.IntegerField(default=2016)
    batch_id = models.ForeignKey(Batch, null=True, blank=True, on_delete=models.CASCADE)
    cpi = models.FloatField(default=0)
    category = models.CharField(max_length=10, null=False)
    father_name = models.CharField(max_length=40, default="", null=True)
    mother_name = models.CharField(max_length=40, default="", null=True)
    hall_no = models.IntegerField(default=0)
    room_no = models.CharField(max_length=10, blank=True, null=True)
    specialization = models.CharField(max_length=40, null=True, default="")
    curr_semester_no = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = "academic_information_student"

    def __str__(self):
        username = str(self.id.user.username)
        return username


class GlobalsFaculty(models.Model):
    id = models.OneToOneField(
        GlobalsExtrainfo, on_delete=models.CASCADE, primary_key=True
    )

    def __str__(self):
        return str(self.id)

    class Meta:
        managed = False
        db_table = "globals_faculty"
