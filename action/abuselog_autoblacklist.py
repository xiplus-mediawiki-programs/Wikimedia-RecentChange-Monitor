# -*- coding: utf-8 -*-
import os
import traceback

import dateutil

os.chdir(os.path.dirname(os.path.abspath(__file__)))

os.environ['TZ'] = 'UTC'


def main(M, log):
    try:
        blackuser = log["user"] + "|" + M.wiki

        message = '{0}於{1}觸發{2}：{3}（{4}）'.format(
            M.link_user(log["user"]),
            M.link_page(log["title"]),
            M.link_abusefilter(log["filter_id"]),
            log["filter"],
            M.link_abuselog(log["id"]) + (
                "|" + M.link_diff(log["revid"])
                if "revid" in log and log["revid"] != ""
                else ""
            )
        )

        rows = M.check_user_blacklist(log["user"])
        if len(rows) != 0:
            blackuser = log["user"] + "|" + rows[0][3]
            message += (
                "\n（黑名單：\u200b" + M.parse_wikicode(rows[0][0]) + "\u200b")
            if rows[0][2] != "" and rows[0][2] != log["user"]:
                message += "，\u200b" + rows[0][2] + "\u200b"
                blackuser = rows[0][2] + "|" + rows[0][3]
            message += '，{0}，{1}p）'.format(
                M.formattimediff(rows[0][1]), rows[0][4])

        on_watch = M.check_abusefilter_watch(af_name=log["filter"])
        on_blacklist = M.check_abusefilter_blacklist(af_name=log["filter"])

        if (len(rows) != 0
                or on_watch
                or on_blacklist):
            M.sendmessage(
                message,
                blackuser,
                log["title"] + "|" + M.wiki
            )

        if on_blacklist:
            reason = "觸發過濾器：" + log["filter"]
            rows = M.check_user_blacklist_with_reason(log["user"], reason)
            if len(rows) == 0:
                M.addblack_user(
                    log["user"],
                    str(int(dateutil.parser.parse(log["timestamp"])
                                    .timestamp())),
                    reason,
                    msgprefix="自動"
                )
            M.adduser_score(M.user_type(log["user"]), 10)

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
