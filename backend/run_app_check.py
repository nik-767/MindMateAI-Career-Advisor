import os
import traceback
import backend.database as database

print('Database module loaded')
print('_HAS_PG =', getattr(database, '_HAS_PG', None))
print('ROLES_FILE =', getattr(database, '_ROLES_FILE', None))
print('roles file exists =', os.path.exists(getattr(database, '_ROLES_FILE', '')))

print('\nCalling init_db()...')
try:
    database.init_db()
    print('init_db() completed')
except Exception as e:
    print('init_db() raised:')
    traceback.print_exc()

print('\nDone')
