from faker import Faker
import random

from main.models import Notes,NotesChoices,userID,MoneyNotesUser

def create_fake_notes(n):

    
    user_id_obj = userID.objects.get(user_id="user-1")
    user_obj = MoneyNotesUser.objects.get(user_id=user_id_obj)

    
    for i in range(n):

        note = Notes(user_id=user_id_obj,
                        user_details = user_obj,
                        date = Faker().date_object().strftime("%d-%m-%Y"),
                        amount = random.randint(1,1_00_000),
                        amount_type = random.choice(NotesChoices.labels),
                        description = "".join(Faker().random_letters(length=10)))

        note.save()
        
    print(Notes.objects.filter(user_id=user_id_obj)[25].id)