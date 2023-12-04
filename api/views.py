from api import signals
from api.db.init_db import init_db

from education.background_thread import start_background_thread
from education.settings import INIT_DB, ENABLE_BACKGROUND_THREAD

if INIT_DB:
    init_db()

if ENABLE_BACKGROUND_THREAD:
    start_background_thread()

signals.signals()
