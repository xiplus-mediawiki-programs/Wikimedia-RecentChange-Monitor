# -*- coding: utf-8 -*-
import os
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))

os.environ['TZ'] = 'UTC'


def main(M, log):
    try:
        if log['type'] != 'abuselog':
            return

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

        if log['wiki'] != M.defaultwiki:
            message += '(' + log['wiki'] + ')'

        user_blacklist = M.check_user_blacklist(log["user"])
        if len(user_blacklist) != 0:
            row = user_blacklist[0]
            blackuser = log["user"] + "|" + row[3]
            message += (
                "\n（黑名單：" + M.parse_wikicode(row[0]))
            if row[2] != "" and row[2] != log["user"]:
                message += "，" + M.link_user(row[2])
                blackuser = row[2] + "|" + row[3]
            message += '，{0}，{1}p）'.format(
                M.formattimediff(row[1]), row[4])

        on_watch = M.check_abusefilter_watch(af_name=log["filter"], wiki=log['wiki'])
        on_af_blacklist = M.check_abusefilter_blacklist(af_name=log["filter"], wiki=log['wiki'])
        user_whitelist = M.check_user_whitelist(log["user"])

        if not user_whitelist and (
                len(user_blacklist) != 0
                or on_watch
                or on_af_blacklist):
            M.sendmessage(
                message,
                blackuser,
                log["title"] + "|" + M.wiki
            )

        if on_af_blacklist:
            reason = "觸發過濾器：" + log["filter"]
            rows = M.check_user_blacklist_with_reason(log["user"], reason, white=True)
            if len(rows) == 0:
                M.addblack_user(
                    log["user"],
                    log["timestamp"],
                    reason,
                    msgprefix="自動"
                )
            M.adduser_score(M.user_type(log["user"]), 10)

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
