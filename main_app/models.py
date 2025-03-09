from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import Group
from django.utils import timezone



class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, password2=None):
        """
        Creates and saves a User with the given email, first_name, last_name and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email      = models.EmailField(verbose_name="Email", max_length=250, unique=True)
    first_name = models.CharField(max_length=250)
    last_name  = models.CharField(max_length=250)
    tc         = models.BooleanField(default=False)
    erp_code   = models.CharField(max_length=10)
    is_active  = models.BooleanField(default=True)
    is_admin   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects    = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    
    def get_full_name(self):
        return self.first_name+ " " + self.last_name


class Level(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=250, null=True, blank=True)
    def __str__(self):
        return str(self.level)

class Role(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    group=models.ForeignKey(Group,on_delete=models.CASCADE,null=True,blank=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.user.get_full_name())+' as '+str(self.level)
    

class ActivityLog(models.Model):
    module = models.CharField(max_length=100, blank=True, null=True)
    sub_module = models.CharField(max_length=100, blank=True, null=True)
    heading = models.TextField()
    activity = models.TextField()
    user_id = models.IntegerField()
    email = models.CharField(max_length=150)
    icon = models.CharField(max_length=100, blank=True, null=True)
    platform = models.CharField(max_length=50)
    platform_icon = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.email + ' ' + self.heading)
    
class PricingPlan(models.Model):
    plan = models.CharField(max_length=20, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def remaining_days(self):
        now = timezone.now()
        return (self.end_time - now).days

    def __str__(self):
        return str(self.plan + " " + self.user.email)

    def save(self, *args, **kwargs):
        if not self.start_time:
            self.start_time = timezone.now()
        if not self.end_time:
            self.end_time = self.start_time + timezone.timedelta(days=28)
        super().save(*args, **kwargs)
