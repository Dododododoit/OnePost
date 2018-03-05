import os

SECRET_KEY = b'\xd5\xab\xd7\xd8M\xc8Nn\xfc\xf4\x88\xf7\xde\xb5D\xde\xb97\x18M\x81\x81\xf7\xe8'

DATABASE_FILENAME = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'var', 'OnePost.sqlite3')
