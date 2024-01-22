from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

from apps.events.models import Category, Interests, PermanentEvent, TemporaryEvent, EventBanner, EventWeek
from apps.locations.models import Address
from apps.profiles.models import Organizer
from apps.users.models import CustomUser


def send_verification_mail(email):
    generated_code = get_random_string(6, '0123456789')
    user = CustomUser.objects.get(email=email)
    user.code = generated_code
    user.save()
    subject = 'Your verification code'
    message = f'Your verification code:\n{generated_code}\nThanks for using our application.'
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, [email])

# from faker import Faker
#
# fake = Faker()
#
# for num in range(500):
#     organizer = Organizer.objects.order_by('?').first()
#     category_instance = Category.objects.order_by('?').first()
#     interests_instance = Interests.objects.order_by('?').first()
#     address_instance = Address.objects.order_by('?').first()
#     generate = PermanentEvent.objects.create(title=fake.catch_phrase(), description=fake.text(),
#                                              price=fake.random_int(min=0, max=100, step=1),
#                                              organizer=organizer, address=address_instance)
#     generate2 = TemporaryEvent.objects.create(title=fake.catch_phrase(), description=fake.text(),
#                                               price=fake.random_int(min=0, max=100, step=1),
#                                               organizer=organizer, address=address_instance)
#     generate.category.set([category_instance])
#     generate.interests.set([interests_instance])
#     generate2.category.set([category_instance])
#     generate2.interests.set([interests_instance])
#
#     # Добавляем 10 EventBanner для каждого события
#     for _ in range(10):
#         EventBanner.objects.create(event=generate, image='image.png')
#         EventBanner.objects.create(event=generate2, image='image.png')
#
#     # Добавляем 10 EventWeek для каждого PermanentEvent
#     for _ in range(10):
#         EventWeek.objects.create(perm=generate, week=fake.name(), start_time='21:18:1',
#                                  end_time='20:18:12', slug='sreda')
#
#     # Добавляем 10 EventDate для каждого TemporaryEvent
#     for _ in range(10):
#         EventDate.objects.create(temp=generate2, start_date='2024-01-20 21:03:22',
#                                  end_date='2024-01-20 22:03:22')