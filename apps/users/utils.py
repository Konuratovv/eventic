import json

from asgiref.sync import sync_to_async
from decouple import config
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

from apps.notifications.models import FollowPerm, FollowTemp
from apps.profiles.models import User
from apps.users.models import CustomUser
import redis


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
    #     language_instance = Language.objects.order_by('?').first()
    #     city_obj = City.objects.all().first()
    #     generate = PermanentEvent.objects.create(title=fake.catch_phrase(), description=fake.text(),
    #                                              price=fake.random_int(min=0, max=100, step=1),
    #                                              organizer=organizer, address=fake.text(), city=city_obj,
    #                                              category=category_instance)
    #     generate2 = TemporaryEvent.objects.create(title=fake.catch_phrase(), description=fake.text(),
    #                                               price=fake.random_int(min=0, max=100, step=1),
    #                                               organizer=organizer, address=fake.text(), city=city_obj,
    #                                               category=category_instance)
    #     # generate.category.set([category_instance])
    #     generate.interests.set([interests_instance])
    #     generate2.interests.set([interests_instance])
    #     generate.language.set([language_instance])
    #     generate2.language.set([language_instance])
    #
    #     # Добавляем 10 EventBanner для каждого события
    #     for _ in range(10):
    #         EventBanner.objects.create(event=generate, image='image.png')
    #         EventBanner.objects.create(event=generate2, image='image.png')
    #
    #     # Добавляем 10 EventWeek для каждого PermanentEvent
    #
    #     for _ in range(10):
    #         time = PermanentEventDays.objects.create(end_time='22:03:22', start_time='22:03:22',
    #                                                  permanent_event=generate, event_week='ПН')
    #
    #     # Добавляем 10 EventDate для каждого TemporaryEvent
    #     for _ in range(10):
    #         EventDate.objects.create(temp=generate2, start_time='21:03:22', end_time='21:03:22', date='2024-01-20')


# def post(data):
#     r = redis.Redis(host='localhost', port=6379, db=0)
#     data_str = json.dumps(data)
#     r.hset('user_connections', 'data', data_str)
#
#     data1 = r.hgetall("user_connections")
#     print(f'то что мне нужна{data1}')

r = redis.Redis(host='redis', port=config('REDIS_PORT'), db=config('REDIS_DB'), password=config('REDIS_PASSWORD'),
                username=config('REDIS_USER'))


def add_to_redis_dict(key, new_data):
    existing_data = r.hgetall(key)

    if not existing_data:
        existing_data = {}

    existing_data.update(new_data)

    r.hmset(key, existing_data)


def delete_from_redis_dict(key, delete_keys):
    existing_data = r.hgetall(key)

    delete_keys_bytes = [bytes(delete_key, 'utf-8') for delete_key in delete_keys]

    for delete_key in delete_keys_bytes:
        if delete_key in existing_data:
            del existing_data[delete_key]

    r.hdel(key, *delete_keys_bytes)

# def check_is_seen_status(email):
#     user = User.objects.get(email=email)
#     follows_perms = FollowPerm.objects.filter(user=user)
#     follows_temps = FollowTemp.objects.filter(user=user)
#     for follow_perm in follows_perms:
#         for notification in follow_perm.notifications.all():
#             if not notification.is_seen:
#                 notification.is_sent = False
#                 notification.save()
#     for follow_temp in follows_temps:
#         for notification in follow_temp.notifications.all():
#             if not notification.is_seen:
#                 notification.is_sent = False
#                 notification.save()
