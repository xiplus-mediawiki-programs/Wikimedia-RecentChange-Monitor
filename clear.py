# -*- coding: utf-8 -*-
import time

from clear_config import recordkept
from Monitor import Monitor


M = Monitor()
M.log("running clear", logtype="clear")

dbs = [
    'bot_message',
    'error',
    'log',
    'RC_142',
    'RC_categorize',
    'RC_edit',
    'RC_log_abusefilter_modify',
    'RC_log_abuselog',
    'RC_log_block',
    'RC_log_delete',
    'RC_log_delete_restore',
    'RC_log_delete_revision',
    'RC_log_gblblock',
    'RC_log_gblrename',
    'RC_log_globalauth',
    'RC_log_merge',
    'RC_log_move',
    'RC_log_newusers',
    'RC_log_patrol',
    'RC_log_protect',
    'RC_log_protect_move_prot',
    'RC_log_protect_unprotect',
    'RC_log_renameuser',
    'RC_log_rights',
    'RC_log_thanks',
    'RC_log_upload',
    'RC_new'
]

timestamp = str(int(time.time() - recordkept))

for db in dbs:
    rows = M.cur.execute(f"""DELETE FROM {db} WHERE `timestamp` < %s""",
                         (timestamp))
    M.db.commit()
    print(f"delete {rows} rows from {db}")
