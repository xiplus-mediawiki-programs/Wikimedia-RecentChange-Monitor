import sys
import os
sys.path.insert(
    0, os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../"))
from Monitor import *  # noqa: E402


M = Monitor()

M.cur.execute(
    """
    SELECT `val` AS `user`, `user_score`.`userhash`, 'black_ipv4' AS `table`
    FROM `black_ipv4`
    LEFT JOIN `user_score` ON `black_ipv4`.`userhash` = `user_score`.`userhash`
    WHERE `point` <= 0
    UNION
    SELECT `val` AS `user`, `user_score`.`userhash`, 'black_ipv6' AS `table`
    FROM `black_ipv6`
    LEFT JOIN `user_score` ON `black_ipv6`.`userhash` = `user_score`.`userhash`
    WHERE `point` <= 0
    UNION
    SELECT `user`, `user_score`.`userhash`, 'black_user' AS `table`
    FROM `black_user`
    LEFT JOIN `user_score` ON `black_user`.`userhash` = `user_score`.`userhash`
    WHERE `point` <= 0
    """, ())
rows = M.cur.fetchall()

for row in rows:
    user = row[0]
    userhash = row[1]
    table = row[2]
    print(user, userhash, table)
    M.cur.execute(
        """DELETE FROM `{}`
        WHERE `userhash` = %s""".format(table),
        (userhash)
    )
    M.db.commit()


M.cur.execute(
    """DELETE FROM `black_page` WHERE `point` = 0"""
)
M.db.commit()
