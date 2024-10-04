import os

from insync.githash import githash

HOT_RELOAD_ENABLED = os.getenv("HOT_RELOAD_ENABLED", "True").lower() == "true"
AUTHS = [tuple(a.split(':')) for a in os.getenv("INSYNC_AUTHS", "zak:kaz;admin:skunk").split(";")]
DB_STR = os.environ.get('INSYNC_DB_STR', 'test.db')

__githash__ = githash()
