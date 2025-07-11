from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
import django.utils.timezone as timezone

# Create your models here.

class userID(models.Model):
    user_id = models.CharField(verbose_name="userID",unique=True, blank=False, max_length=20,primary_key=True)
    def __str__(self):
        return f"OBJ: {self.user_id}"
    
class MoneyNotesUserManager(BaseUserManager):

    def create_user(self, first_name, last_name, user_name, email, password=None, **kwargs):

        if not user_name:
            raise ValueError("username must be set")
        if not email:
            raise ValueError("Email must be set")
        if not first_name:
            raise ValueError("first name must be set")
        
        email = self.normalize_email(email=email)
        last_user = userID.objects.order_by('user_id').last()
        if last_user:
            new_id_number = int(last_user.user_id.split('-')[1]) + 1
        else:
            new_id_number = 1
    
        new_user_id = f"user-{new_id_number}"
        user_id_obj = userID.objects.create(user_id=new_user_id)
        user:models.Model = self.model(user_id=user_id_obj, first_name=first_name, last_name=last_name,
                                       user_name=user_name, email=email, **kwargs)
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_superuser(self, first_name, last_name, user_name, email, password=None, **kwargs):
        kwargs.setdefault("is_staff",True)
        kwargs.setdefault("is_superuser",True)
        kwargs.setdefault("is_active",True)

        return self.create_user(first_name=first_name,last_name=last_name,user_name=user_name,
                                email=email,password=password, **kwargs)

    
class MoneyNotesUser(AbstractBaseUser,PermissionsMixin):

    user_id = models.OneToOneField(to=userID, on_delete=models.CASCADE, related_name="MoneyNotesUser_user_id",primary_key=True)
    first_name = models.CharField(verbose_name="firstName", blank=False, max_length=50)
    last_name = models.CharField(verbose_name="lastName", blank=True, max_length=50)
    user_name = models.CharField(verbose_name="userName", unique=True, blank=False, max_length=25)
    email = models.EmailField(verbose_name="email", unique=True, blank=False,
                              validators=[validators.EmailValidator])
    password = models.CharField(verbose_name="password", blank=False,max_length=1000)

    first_login = models.DateTimeField(verbose_name="firstLogin", default=timezone.now)
    last_login  = models.DateTimeField(verbose_name="lastLogin",  default=timezone.now)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = MoneyNotesUserManager()
    
    USERNAME_FIELD = "user_name"
    REQUIRED_FIELDS = ["email","first_name","last_name"]

    def __str__(self):
        return f"OBJ: {self.user_id.user_id} -> {self.user_name} -> {self.email}"
    
    class Meta:
        ordering = ["first_login"]

class NotesChoices(models.TextChoices):
    INCOME = "Income", "Income",
    EXPENDITURE = "Expenditure", "Expenditure"

class Notes(models.Model):

    user_id = models.ForeignKey(to=userID, on_delete=models.CASCADE, related_name="Notes_user_id")
    user_details = models.ForeignKey(to=MoneyNotesUser, on_delete=models.CASCADE, related_name="Notes_user_details")
    
    date = models.DateField(verbose_name="date",blank=False, null=False)
    amount = models.FloatField(verbose_name="amount", blank=False, null=False)
    amount_type = models.CharField(verbose_name="amountType", 
                                   choices=NotesChoices.choices,max_length=50,blank=False,null=False)
    description = models.TextField(verbose_name="description",blank=True,null=True)

    def __str__(self):
        return f"OBJ: {self.user_id.user_id} -> {self.user_details.user_name} -> {self.user_details.email} -> {self.date} -> {self.amount} -> {self.amount_type}"

    class Meta:
        ordering = ["-date"]



def get_delete_time():
    return timezone.now() + timezone.timedelta(minutes=10)

class EmailVerification(models.Model):

    first_name = models.CharField(verbose_name="firstName", blank=False, max_length=50)
    last_name = models.CharField(verbose_name="lastName", blank=True, max_length=50)
    user_name = models.CharField(verbose_name="userName", unique=True, blank=False, max_length=25)
    email = models.EmailField(verbose_name="email", unique=True, blank=False,
                              validators=[validators.EmailValidator])
    password = models.CharField(verbose_name="password", blank=False,max_length=1000)
    created_date_time = models.DateTimeField(verbose_name="createdDateTime", default=timezone.now)
    delete_date_time = models.DateTimeField(verbose_name="deleteDateTime", default=get_delete_time)
    is_verified = models.BooleanField(verbose_name="isVerified",default=False)