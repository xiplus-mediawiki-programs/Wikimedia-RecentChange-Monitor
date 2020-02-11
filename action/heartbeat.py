import os
import sys
import time

sys.path.insert(0, os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../"))
from Monitor import Monitor  # noqa: E402, pylint: disable=C0413


M = Monitor()

dbs = [
    ('RC_edit', 600),
    ('RC_log_abuselog', 3600),
    ('rc_newusers_autocreate', 3600),
]

timestamp = int(time.time())

for db in dbs:
    M.db_execute(f"""SELECT `timestamp` FROM {db[0]} ORDER BY `timestamp` DESC LIMIT 1""")
    row = M.db_fetchone()
    timediff = timestamp - row[0]
    print(db[0], timediff)
    if timediff > db[1]:
        msg = '{}已有{}秒未收到訊息'.format(db[0], timediff)
        M.sendmessage(msg, chat_id=M.admin_chat_id, nolog=True)
