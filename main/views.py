from django.shortcuts import render,redirect,HttpResponse
from django.core import serializers
from django.core.handlers.wsgi import WSGIRequest
from django.contrib import messages
from django.utils import timezone

from .models import userID,MoneyNotesUser,Notes,NotesChoices,EmailVerification
from django.db.models import Q,functions,aggregates
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import BaseUserManager

from django.core.mail import EmailMessage
from django.conf import settings

from django.core.paginator import Paginator

import random
import re
import datetime
import schedule
import threading
import time
import base64

regular_expression_for_password = "(?=.*[a-z])(?=.*[A-Z)(?=.*[0-9])(?=.*[!@#$%^&*()_+]).{8,}"
# Create your views here.


@staticmethod
def delete_emails_from_email_verification_db():
    # using the schedular
    query_sets = EmailVerification.objects.all()
    for each_query in query_sets:
        if each_query.delete_date_time < timezone.now():
            each_query.delete()

def schedule_task():
    schedule.every(5).minutes.do(delete_emails_from_email_verification_db)
    while True:
        schedule.run_pending()
        five_minutes_in_seconds = 60 * 5
        time.sleep(five_minutes_in_seconds)

t1 = threading.Thread(target=schedule_task, daemon=True)
t1.start()

def login_page(request:WSGIRequest):

    if request.session.get("is_login",False):
        if update_last_login(request):
            return redirect(to="get_data")

    elif request.method == "POST" and request.session.get("is_login",False):
        if update_last_login(request):
            return render(request=request, template_name="main_get_data.html")
    
    elif request.method == "POST":
        username_or_email = request.POST.get("user-name")
        password = request.POST.get("password").strip()
        data_list = {}
        for key,value in request.POST.items():
            if "-" in key:
                data_list[key.replace("-","_")] = value
            else:
                data_list[key] = value

        query_set = MoneyNotesUser.objects.filter(user_name = username_or_email) |\
                    MoneyNotesUser.objects.filter(email = username_or_email)
        
        if not query_set.exists():
            messages.warning(request, message="No username or Email found")
            return render(request=request, template_name="main_login.html", context=data_list)
        
        user_name = query_set[0].user_name
        user = authenticate(request=request, username=user_name, password=password)
        if not user:
            messages.warning(request, message="Password does not match")
            return render(request=request, template_name="main_login.html", context=data_list)
        

        request.session.set_expiry(datetime.timedelta(days=7))
        request.session["is_login"] = True
        request.session["user_name"] = user_name
        update_last_login(request)
        login(request=request,user=user)
        return redirect("get_data")

    return render(request=request,
                  template_name="main_login.html")

def create_account_page(request:WSGIRequest):
    if request.method == "POST":
        messages.get_messages(request).used = True # removes all the messages
        
        data_list= {}
        for key,value in request.POST.items():
            if "-" in key:
                data_list[key.replace("-","_")] = value.strip()
            else:
                data_list[key]= value.strip()

        first_name:str = data_list["first_name"]
        last_name:str = data_list["last_name"]
        user_name:str = data_list["user_name"]
        email:str     = data_list["email"]
        password1:str = data_list["password1"]
        password2:str = data_list["password2"]

        if MoneyNotesUser.objects.filter(user_name = user_name):
            messages.warning(request, message="User name already taken.")
        else:
            if " " in user_name:
                messages.warning(request,message="username can't contains space")

        if MoneyNotesUser.objects.filter(email = email).exists():
            messages.warning(request, message="Email already in use")

        if not re.fullmatch(pattern=regular_expression_for_password, string=password1):
            messages.warning(request, message="Password pattern not match")
        if password1 != password2:
            messages.warning(request, message="password1 and password2 not match")

        if messages.get_messages(request):
            return render(request=request, template_name="main_create_account.html", context=data_list)
        else:
            url = f"{request.build_absolute_uri().replace(request.get_full_path(),"")}/verify-email/{email}"
            subject = "verify email from Money Notes"
            message = f""" 
            <!DOCTYPE html>
            <html>
            <body>
                <p>Hello {user_name}</p>
                <p>Please click the button below to confirm:</p>
                <a href="{url}"
                style="background-color:#007bff; color:white; padding:10px 20px; text-decoration:none; border-radius:4px;">
                Confirm Now
                </a>
                <br>
                <br>
                <strong>Expires at {timezone.localtime(timezone.now()+timezone.timedelta(minutes=10))}</strong>
                <p>Thank you!</p>
            </body>
            </html>
            """
            try:
                filter_emails = EmailVerification.objects.filter(email=email)
                if filter_emails.exists():
                    for email in filter_emails:
                        email.delete()

                password1:bytes = password1.encode()
                email = BaseUserManager.normalize_email(email)
                encrypted_password = base64.b64encode(password1).decode()
                email_verification = EmailVerification(first_name=first_name, last_name=last_name, user_name=user_name, 
                                                       email=email, password=encrypted_password)

                email_verification.clean_fields()
                email_verification.save()
                send_email(email=email, subject=subject, message=message, is_verification=True)
                messages.success(request, message="Verification mail send successfully")
                messages.success(request, message="verify email")

            except Exception as e:
                messages.error(request, message=e)

            return redirect(to="create_account")
   

    return render(request=request,
                  template_name="main_create_account.html")

def delete_account(request:WSGIRequest):
    data_dict = {"user_name":request.session.get("user_name")}
    if request.method == "POST":
        user_name = request.POST.get("text").strip().split(" ")[-1]
        user_id = MoneyNotesUser.objects.get(user_name=user_name).user_id.user_id
        userID.objects.get(user_id=user_id).delete()
        request.session.clear()
        return redirect("login_page")
    
    return render(request=request, template_name="./delete_account.html",context=data_dict)

def verify_email(request:WSGIRequest,email):
    # before login verifying the email
    query_set = EmailVerification.objects.filter(email=email)
    
    if query_set.exists() and query_set[0].delete_date_time > timezone.now():
        query_set = query_set[0]

        if query_set.is_verified:
            messages.success("Link already verified")
            return redirect("login_page")

        first_name = query_set.first_name
        last_name = query_set.last_name
        user_name = query_set.user_name
        encrypted_password_b:str = query_set.password.encode()
        password = base64.b64decode(encrypted_password_b).decode()

        last_user_id_obj:userID = userID.objects.filter().order_by("user_id").last()
        if last_user_id_obj:
            last_user_id:str = last_user_id_obj.user_id
            new_user_id = "user-" + str(int(last_user_id.split("-")[1])+1)
        else:
            new_user_id = "user-1"

        user_id_obj = userID.objects.create(user_id=new_user_id)
        user = MoneyNotesUser(user_id=user_id_obj,first_name=first_name,last_name=last_name,
                    user_name=user_name,email=email) 
        user.set_password(password)
        try:
            user.clean_fields()
            user.save()

            query_set.is_verified = True
            query_set.save() # saved in db

            messages.success(request, message="Created Account Successfully")
            return redirect(to="login_page")
        except Exception as e:
            messages.warning(request, message=e)
            return redirect(to="create_account")

    messages.success(request, message="Time Out! or No email Found")
    return redirect(to="create_account")



def forgot_password(request:WSGIRequest):
    if request.method == "POST" and request.POST.get("form-type") == "send-otp":
        given_user_name_or_email = request.POST.get('user-name-or-email')
        
        query_set = MoneyNotesUser.objects.filter(user_name = given_user_name_or_email) |\
                    MoneyNotesUser.objects.filter(email = given_user_name_or_email)

        if not query_set.exists():
            messages.warning(request, message="No username or Email found")
            return redirect("forgot_password")
        
        request.session["user_name_or_email"] = given_user_name_or_email
        request.session["query_set"] = serializers.serialize("json",queryset=query_set)

        user_email = query_set[0].email
        return redirect(to="send_otp", email=user_email)
    
    elif request.method == "POST" and request.POST.get("form-type") == "verify":
        entered_otp = request.POST.get("otp-value")
        return redirect(to="verify_otp", entered_otp=entered_otp)
    
    elif request.method == "POST" and request.POST.get("form-type") == "update-password":

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not request.session.items():
            messages.warning(request, message="Session Expired")
            return redirect("forgot_password")
        
        if not re.fullmatch(pattern=regular_expression_for_password, string=password1):
            messages.warning(request, message="Password should contains")
            messages.warning(request, message="one lower case letter")
            messages.warning(request, message="one upper case letter")
            messages.warning(request, message="one numeric")
            messages.warning(request, message="one special char of !@#$%^&*()_+")
            messages.warning(request, message="password length min 8 char")

        elif password1 != password2:
            messages.warning(request, message="Password 1 and Password 2 not matched")
        
        
        if messages.get_messages(request):
            return redirect(to="forgot_password")
        
        else:
            # update in django models
            json_query_set = request.session.get("query_set",False)
            if not json_query_set:
                messages.warning(request, message="Session Expired")
                return redirect("forgot_password")
            
            deserialized_obj = tuple(serializers.deserialize(format="json", stream_or_string=json_query_set))[0]
            query_set:MoneyNotesUser = deserialized_obj.object
            query_set.set_password(password1)
            query_set.save()
            
            send_email(email=query_set.email, subject="Updated successful", message="Password update successfully.")
            request.session.set_expiry(0)
            request.session.clear()
            return redirect(to="login_page")

    user_name_or_email = request.session.get("user_name_or_email",False)
    is_valid = request.session.get("is_valid",False)

    otp_sent = True if user_name_or_email else False
    
    return render(request=request,
                template_name="main_forgot_password.html",
                context={"user_name_or_email":user_name_or_email, "otp_sent":otp_sent, "is_valid":is_valid})

def send_otp(request:WSGIRequest, email):
    if (not request.session.get("user_name_or_email",False)):
        messages.warning(request, message="Session Expired")
        return redirect(to="forgot_password")
    
    random_otp_value = str(random.randint(1_00_000,10_00_000))
    subject = "OTP"
    message = f"The OTP for the update password\nOTP value: {random_otp_value}\nDon't share your OTP with others"
    
    send_email(email=email, subject=subject, message=message)
    request.session["otp"] = random_otp_value
    request.session.set_expiry(175)

    messages.success(request, message="OTP send successfully")

    return redirect("forgot_password")

def send_email(email,subject,message,files:list=None,is_verification=False):
    email_obj = EmailMessage(subject=subject,
                             body=message,
                             from_email=settings.EMAIL_HOST_USER,
                             to=[email])
    if is_verification:
        email_obj.content_subtype = "html"

    if files:
        for file in files:
            email_obj.attach_file(file)

    email_obj.send(fail_silently=True)

def verify_otp(request:WSGIRequest, entered_otp):

    given_otp = request.session.get("otp")
    if not given_otp:
        messages.warning(request, message="Session Expired")

    is_valid = False

    if given_otp == entered_otp:
        is_valid = True
    
    request.session["is_valid"] = is_valid
    if given_otp != None and not is_valid:
        messages.warning(request, message="Incorrect OTP")
        
    return redirect(to="forgot_password")

@login_required(login_url="/")
def logout_page(request:WSGIRequest):
    logout(request=request)
    request.session.set_expiry(0)
    request.session.clear()
    return redirect(to="login_page")


@staticmethod
def update_last_login(request:WSGIRequest):
    try:
        user_name = request.session.get("user_name",False)
        money_notes_user_obj:MoneyNotesUser = MoneyNotesUser.objects.get(user_name=user_name)
        money_notes_user_obj.last_login = timezone.now()
        money_notes_user_obj.save()
        return True
    except:
        request.session.clear()
        return False


@staticmethod
def format_in_ind_currency(amount) -> str:

    if amount < 0:
        amount = abs(amount)

    if 0 <= amount < 1_000:
        return str(amount)
    
    amount = f"{amount:.2f}"

    number_part,fraction_part = amount.split(".")
    first_digits,last_three_digits = number_part[:-3],number_part[-3:]
    
   
    string = ""
    count = 0
    for i in first_digits[::-1]:
        if count == 2:
            count = 0
            string += ","
            string += i
            continue
        string += i
        count += 1
   
    
    formate_string = string[::-1] + "," + last_three_digits + "." + fraction_part
    return formate_string



@login_required(login_url="/")
def add_data(request:WSGIRequest):
    data_list = {}
    user_name = request.session.get("user_name",False)
    if user_name:
        data_list["user_name"] = user_name
    
    if request.method == "POST":

        date = request.POST.get("date")
        amount = request.POST.get("amount")
        choices = NotesChoices.choices
        given_type = int(str(request.POST.get("amount-type")))
        amount_type = choices[given_type][0]
        description = request.POST.get("description")

        user_id = request.session.get("_auth_user_id")

        user_id_obj = userID.objects.get(user_id=user_id)
        user_details_obj = MoneyNotesUser.objects.get(user_id=user_id_obj)

        notes = Notes(user_id=user_id_obj,
                      user_details=user_details_obj,
                      date=date,
                      amount=amount,
                      amount_type=amount_type,
                      description=description)
        try:
            notes.clean_fields()
            notes.save()
            messages.success(request, message="Data Added Successfully")
        except Exception as e:
            messages.warning(request,message="fields not valid")
            messages.warning(request,message=e)

        return redirect(to="add_data")

    return render(request=request,
                  template_name="main_add_data.html", context=data_list)


@login_required(login_url="/")
def get_data(request:WSGIRequest):
    data_list = {}   

    user_name = request.session.get("user_name",False)
    if user_name:
        data_list["user_name"] = user_name

    query_set = Notes.objects.filter(user_id=request.session.get("_auth_user_id"))

    
    data_list["filter_options"] = False
    if request.method == "GET" and len(request.GET.dict()) > 1:
        from_date = request.GET.get("from-date")
        to_date= request.GET.get("to-date")
        sorting = request.GET.get("sorting")
        group_by = request.GET.get("group-by")
        amt_type = request.GET.get("amt-type")

        data_list["filter_options"] = True
        data_list["from_date"] = from_date
        data_list["to_date"] = to_date
        data_list["sorting"] = sorting
        data_list["group_by"] = group_by
        data_list["amt_type"] = amt_type

        copied_data = data_list.copy()
        copied_data.pop("user_name")
        data_list["all_options"] = ""
        for key,value in copied_data.items():
            data_list["all_options"] += f"&{key.replace("_","-")}={value}"

    if request.GET.get("sorting",False) and request.GET.get("sorting") != "none":
        string = "amount" if request.GET.get("sorting") == "asc" else "-amount"
        query_set = query_set.order_by(string)

    if data_list["filter_options"]:
        if data_list["amt_type"] != "none":
            query_set = query_set.filter(amount_type = data_list["amt_type"])

        if data_list["from_date"] and data_list["to_date"]:
            query_set = query_set.filter(date__gte = data_list["from_date"])
            query_set = query_set.filter(date__lte = data_list["to_date"])
        elif data_list["from_date"]:
            query_set = query_set.filter(date__gte = data_list["from_date"])
        elif data_list["to_date"]:
            query_set = query_set.filter(date__lte = data_list["to_date"])

        total_income = query_set.filter(amount_type="Income").aggregate(total = aggregates.Sum("amount"))["total"] or 0
        total_expenditure = query_set.filter(amount_type="Expenditure").aggregate(total = aggregates.Sum("amount"))["total"] or 0
        grand_total = total_income - total_expenditure
        
        total_income = format_in_ind_currency(total_income)
        total_expenditure = format_in_ind_currency(total_expenditure)
        grand_total_formate = format_in_ind_currency(grand_total)

        data_list["total_income"] = total_income
        data_list["total_expenditure"] = total_expenditure
        data_list["grand_total"] = grand_total
        data_list["grand_total_formate"] = grand_total_formate

        if data_list["group_by"] != "none":

            month_key_value = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
            quarter_key_value = {1:"Jan-Mar",2:"Apr-Jun",3:"Jul-Sep",4:"Oct-Dec"}
            
            data_list["total_income"] = data_list["total_expenditure"] = data_list["grand_total"] = data_list["grand_total_formate"] = 0
            data_list_group_by = []

            if data_list["group_by"] == "month":
                main_query = query_set.annotate(grouped=functions.ExtractMonth("date"))
            elif data_list["group_by"] == "quarter":
                main_query = query_set.annotate(grouped=functions.ExtractQuarter("date"))
            elif data_list["group_by"] == "year":
                main_query = query_set.annotate(grouped=functions.ExtractYear("date"))

            if data_list["group_by"] in ["month","quarter","year"]:
                years_or_month_or_quarters = sorted(set(main_query.values_list("grouped",flat=True).distinct()))
                query1 = dict(main_query.filter(amount_type="Income").values('grouped')\
                                        .annotate(total_amount=aggregates.Sum('amount')).order_by('grouped').values_list("grouped","total_amount"))
                query2 = dict(main_query.filter(amount_type="Expenditure").values('grouped')\
                                        .annotate(total_amount=aggregates.Sum('amount')).order_by('grouped').values_list("grouped","total_amount"))
            
                for i in years_or_month_or_quarters:
                    income = query1.get(i,0)
                    expenditure = query2.get(i,0)
                    grand_total = income - expenditure
                    grand_total_formate = format_in_ind_currency(grand_total)

                    data_list["total_income"] = data_list.get("total_income",0) + income
                    data_list["total_expenditure"] = data_list.get("total_expenditure",0) + expenditure
                    data_list["grand_total"] = data_list.get("grand_total",0) + grand_total
                    data_list["grand_total_formate"] = format_in_ind_currency(data_list["grand_total"])

                    d = {}
                    if group_by == "month":
                        d["grouped_by"] = month_key_value[i]
                    elif group_by == "quarter":
                        d["grouped_by"] = quarter_key_value[i]
                    else:
                        d["grouped_by"] = i
                    d.update({"income":format_in_ind_currency(income),
                              "expenditure":format_in_ind_currency(expenditure),
                            "grand_total":grand_total,"grand_total_formate":grand_total_formate})
                    data_list_group_by.append(d)
                
                data_list["total_income"] = format_in_ind_currency(data_list["total_income"])
                data_list["total_expenditure"] = format_in_ind_currency(data_list["total_expenditure"])

                keys = list(data_list_group_by[0].keys())
                keys.remove("grand_total_formate")
                keys[0] = group_by 
                data_list["data_list_group_by_keys"] = keys
                query_set = data_list_group_by
            

            elif data_list["group_by"] == "year-quarter":
                year_and_quarter = sorted(set(query_set.annotate(year=functions.ExtractYear("date"),
                                                                 quarter=functions.ExtractQuarter("date"))\
                                            .values_list("year","quarter")))
                query1 = query_set.filter(amount_type="Income")\
                                .annotate(year=functions.ExtractYear("date"),
                                        quarter=functions.ExtractQuarter("date"))\
                                .values("year","quarter").order_by("year","quarter").annotate(total=aggregates.Sum("amount"))
 
                query2 = query_set.filter(amount_type="Expenditure")\
                                .annotate(year=functions.ExtractYear("date"),
                                        quarter=functions.ExtractQuarter("date"))\
                                .values("year","quarter").order_by("year","quarter").annotate(total=aggregates.Sum("amount"))
            
                for year,quarter in year_and_quarter:

                    if query1.filter(Q(year=year) & Q(quarter=quarter)).exists():
                        income = query1.filter(Q(year=year) & Q(quarter=quarter))[0].get("total")
                    else:
                        income = 0
                    if query2.filter(Q(year=year) & Q(quarter=quarter)).exists():
                        expenditure = query2.filter(Q(year=year) & Q(quarter=quarter))[0].get("total")
                    else:
                        expenditure = 0

                    grand_total = income - expenditure
                    grand_total_formate = format_in_ind_currency(grand_total)

                    data_list["total_income"] = data_list.get("total_income",0) + income
                    data_list["total_expenditure"] = data_list.get("total_expenditure",0) + expenditure
                    data_list["grand_total"] = data_list.get("grand_total",0) + grand_total
                    data_list["grand_total_formate"] = format_in_ind_currency(data_list["grand_total"])
                    

                    data_list_group_by.append({"grouped_by":f"{year}/{quarter_key_value[quarter]}",
                                               "income":format_in_ind_currency(income),
                                               "expenditure":format_in_ind_currency(expenditure),
                                               "grand_total":grand_total,"grand_total_formate":grand_total_formate})
                
 
                data_list["total_income"] = format_in_ind_currency(data_list["total_income"])
                data_list["total_expenditure"] = format_in_ind_currency(data_list["total_expenditure"])
                

                keys = list(data_list_group_by[0].keys())
                keys.remove("grand_total_formate")
                data_list["data_list_group_by_keys"] = keys
                query_set = data_list_group_by

            

    paginator_obj  = Paginator(query_set, per_page=15)

    if request.GET.get("page",False):
        page_no = request.GET.get("page")
    else:
        page_no = 1
    
    page = paginator_obj.get_page(number=page_no)
    data_list["page"] = page
    return render(request=request,
                  template_name="main_get_data.html",context=data_list)


@login_required(login_url="/")
def update_record(request:WSGIRequest, id):

    data_list = {}
    user_name = request.session.get("user_name",False)
    if request.method == "POST":
        date = request.POST.get("date")
        amount = request.POST.get("amount")
        choices = NotesChoices.choices
        given_type = int(str(request.POST.get("amount-type")))
        amount_type = choices[given_type][0]
        description = request.POST.get("description")

        user_id = request.session.get("_auth_user_id")

        user_id_obj = userID.objects.get(user_id=user_id)
        user_details_obj = MoneyNotesUser.objects.get(user_id=user_id_obj)

        note = Notes.objects.get(id=id)
        note.date = date
        note.amount = amount
        note.amount_type = amount_type
        note.description = description
        try:
            note.clean_fields()
            note.save()
        except Exception as e:
            messages.warning(request,message="fields not valid")
            messages.warning(request,message=e)

        return redirect(to="get_data")

    if user_name:
        data_list["user_name"] = user_name
    data_list["query_set"] = Notes.objects.get(id=id)

    return render(request=request,
                  template_name="main_update_data.html",context=data_list)

@login_required(login_url="/")
def delete_record(request:WSGIRequest,id,query_url):

    # delete the date from DB
    notes = Notes.objects.get(id=id)
    notes.delete()

    return redirect(to=f"/get-data?{query_url}")