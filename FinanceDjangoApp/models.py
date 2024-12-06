# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Activity(models.Model):
    activityid = models.CharField(db_column='activityID', primary_key=True, max_length=10)  # Field name made lowercase.
    activitytype = models.CharField(db_column='activityType', max_length=7)  # Field name made lowercase.
    userid = models.ForeignKey('Userprofile', models.DO_NOTHING, db_column='userID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Activity'


class Auditlog(models.Model):
    logid = models.AutoField(db_column='logID', primary_key=True)  # Field name made lowercase.
    actiontype = models.CharField(db_column='actionType', max_length=6)  # Field name made lowercase.
    tablename = models.CharField(db_column='tableName', max_length=50)  # Field name made lowercase.
    recordid = models.CharField(db_column='recordID', max_length=50)  # Field name made lowercase.
    actiondate = models.DateTimeField(db_column='actionDate')  # Field name made lowercase.
    details = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'AuditLog'


class Budget(models.Model):
    budgetid = models.CharField(db_column='budgetID', primary_key=True, max_length=15)  # Field name made lowercase.
    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    budgetamount = models.DecimalField(db_column='budgetAmount', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    userid = models.ForeignKey('Userprofile', models.DO_NOTHING, db_column='userID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Budget'


class Category(models.Model):
    categoryid = models.AutoField(db_column='categoryID', primary_key=True)  # Field name made lowercase.
    categoryname = models.CharField(db_column='categoryName', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Category'


class Date(models.Model):
    date = models.DateField(primary_key=True)
    year = models.TextField(blank=True, null=True)  # This field type is a guess.
    quarternumber = models.CharField(db_column='quarterNumber', max_length=45, blank=True, null=True)  # Field name made lowercase.
    quartername = models.CharField(db_column='quarterName', max_length=45, blank=True, null=True)  # Field name made lowercase.
    monthnumber = models.IntegerField(db_column='monthNumber', blank=True, null=True)  # Field name made lowercase.
    monthname = models.CharField(db_column='monthName', max_length=45, blank=True, null=True)  # Field name made lowercase.
    weeknumber = models.IntegerField(db_column='weekNumber', blank=True, null=True)  # Field name made lowercase.
    daynumber = models.IntegerField(db_column='dayNumber', blank=True, null=True)  # Field name made lowercase.
    dayname = models.CharField(db_column='dayName', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Date'


class Expense(models.Model):
    expenseid = models.CharField(db_column='expenseID', primary_key=True, max_length=10)  # Field name made lowercase. The composite primary key (expenseID, budgetID, activityID, date, categoryID) found, that is not supported. The first column is selected.
    payeedetail = models.CharField(db_column='payeeDetail', max_length=200, blank=True, null=True)  # Field name made lowercase.
    remarks = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    budgetid = models.ForeignKey(Budget, models.DO_NOTHING, db_column='budgetID')  # Field name made lowercase.
    activityid = models.ForeignKey(Activity, models.DO_NOTHING, db_column='activityID')  # Field name made lowercase.
    date = models.ForeignKey(Date, models.DO_NOTHING, db_column='date')
    categoryid = models.ForeignKey(Category, models.DO_NOTHING, db_column='categoryID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Expense'
        unique_together = (('expenseid', 'budgetid', 'activityid', 'date', 'categoryid'),)


class Income(models.Model):
    incomeid = models.CharField(db_column='incomeID', primary_key=True, max_length=10)  # Field name made lowercase. The composite primary key (incomeID, activityID, incomeDate, sourceID) found, that is not supported. The first column is selected.
    payerdetail = models.CharField(db_column='payerDetail', max_length=100)  # Field name made lowercase.
    remarks = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    activityid = models.ForeignKey(Activity, models.DO_NOTHING, db_column='activityID')  # Field name made lowercase.
    incomedate = models.ForeignKey(Date, models.DO_NOTHING, db_column='incomeDate')  # Field name made lowercase.
    sourceid = models.ForeignKey('Source', models.DO_NOTHING, db_column='sourceID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Income'
        unique_together = (('incomeid', 'activityid', 'incomedate', 'sourceid'),)


class Source(models.Model):
    sourceid = models.CharField(db_column='sourceID', primary_key=True, max_length=10)  # Field name made lowercase.
    sourcename = models.CharField(db_column='sourceName', max_length=45)  # Field name made lowercase.
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Source'


class Userprofile(models.Model):
    userid = models.CharField(db_column='userID', primary_key=True, max_length=10)  # Field name made lowercase.
    username = models.CharField(db_column='userName', max_length=100)  # Field name made lowercase.
    email = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'UserProfile'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
