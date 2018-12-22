# -*- coding: utf-8 -*-
import traceback
import os
import csv
import json
import dateutil
from Monitor import *
from abuselog_autoblacklist_config import afwatchlist, afblacklist


os.chdir(os.path.dirname(os.path.abspath(__file__)))

os.environ['TZ'] = 'UTC'

M = Monitor()

abusefilter_list = {}
with open(os.path.dirname(os.path.realpath(__file__)) + '/abusefilter_list.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        abusefilter_list[int(row[0])] = row[1]

afwatchlistname = []
for id in afwatchlist:
    afwatchlistname.append(abusefilter_list[id])

afblacklistname = []
for id in afblacklist:
    afblacklistname.append(abusefilter_list[id])


def main(log):
    M = Monitor()
    try:
        print(log["filter"], log["timestamp"])

        message = (
            M.link_user(log["user"]) + '於' + M.link_page(log["title"]) +
            '觸發' + M.link_abusefilter(log["filter_id"]) + '：' +
            log["filter"] + '（' + M.link_abuselog(log["id"])
        )
        if "revid" in log and log["revid"] != "":
            message += "|" + M.link_diff(log["revid"])
        message += '）'

        blackuser = log["user"] + "|" + M.wiki
        rows = M.check_user_blacklist(log["user"])
        if len(rows) != 0:
            blackuser = log["user"] + "|" + rows[0][3]
            message += (
                "\n（黑名單：\u200b" + M.parse_wikicode(rows[0][0]) + "\u200b")
            if rows[0][2] != "" and rows[0][2] != log["user"]:
                message += "，\u200b" + rows[0][2] + "\u200b"
                blackuser = rows[0][2] + "|" + rows[0][3]
            message += '，' + M.formattimediff(rows[0][1]) + "，" + str(rows[0][4]) + "p）"

        if (len(rows) != 0
                or log["filter"] in afwatchlistname
                or log["filter"] in afblacklistname):
            M.sendmessage(
                message,
                log["user"] + "|" + M.wiki,
                log["title"] + "|" + M.wiki
            )

        if log["filter"] in afblacklistname:
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
            M.adduser_score(M.user_type(log["user"]), 10, "abuselog")

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc())
