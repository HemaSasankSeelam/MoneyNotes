from django.contrib import admin

from .models import userID,MoneyNotesUser,Notes,EmailVerification
# Register your models here.

class MoneyNotesUserAdmin(admin.ModelAdmin):
    list_display = ["user_id","first_name","last_name","user_name","email","first_login","last_login"]
    
admin.site.register(model_or_iterable=MoneyNotesUser,
                    admin_class=MoneyNotesUserAdmin)

admin.site.register(model_or_iterable=userID)


class NotesAdmin(admin.ModelAdmin):
    list_display = ["id","user_id","user_details","date","amount","amount_type","description"]

admin.site.register(model_or_iterable=Notes, admin_class=NotesAdmin)


class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ["first_name","last_name","user_name","email","password","created_date_time","delete_date_time"]

admin.site.register(model_or_iterable=EmailVerification, admin_class=EmailVerificationAdmin)