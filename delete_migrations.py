import os
# from apps.users.models import *
from django.core.management import call_command


apps = ['users', 'events', 'favorites', 'invitations', 'locations', 'notifications', 'profiles', 'questions']

sql_file = './db.sqlite3'

for app in apps:
    migration_path = f'./apps/{app}/migrations/'

    for filename in os.listdir(migration_path):
        if filename.endswith('.py') and filename != '__init__.py' and sql_file:
            migration_file = os.path.join(migration_path, filename)
            os.remove(migration_file)
            os.remove(sql_file)
