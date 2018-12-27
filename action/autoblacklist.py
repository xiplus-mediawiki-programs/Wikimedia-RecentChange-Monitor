import traceback
import json
from Monitor import *
from autoblacklist_config import *
from strtotime import strtotime
from time import time
import datetime
import re


def main(change):
    M = Monitor()
    try:
        M.change_wiki_and_domain(change['wiki'], change["meta"]["domain"])

        wiki = change["wiki"]
        ctype = change["type"]
        user = change["user"]
        blackuser = user + "|" + wiki
        title = change["title"]
        comment = change["comment"]

        if wiki not in followwiki:
            return

        if (ctype in ["edit", "new"]
                and change["namespace"] == 3
                and re.match(r"^User talk:", title)
                and re.match(r"^((層級|层级)[1234]|(單層級|单层级)(通知|警告))", comment)
                and not re.search(warnreasonblacklist, comment)
                and user not in warnuserblacklist):
            reason = "被" + user + "警告：" + comment
            target = re.sub(r"^[^:]+:(.+)$", "\\1", title)
            point = 0
            if re.match(r"^(層級|层级)1", comment):
                point = 5
            elif re.match(r"^(層級|层级)2", comment):
                point = 10
            elif re.match(r"^(層級|层级)3", comment):
                point = 15
            elif re.match(r"^(層級|层级)4", comment):
                point = 20
            elif re.match(r"^(單層級通知|单层级通知)：(回退個人的測試|回退个人的测试)", comment):
                point = 10
            elif re.match(r"^(單層級警告|单层级警告)", comment):
                point = 10
            if point > 0:
                M.addblack_user(
                    target, change["timestamp"], reason, msgprefix="自動")
                M.adduser_score(M.user_type(target), point, "autoblacklist/warn")

        if ctype == "log":
            log_type = change["log_type"]
            log_action = change["log_action"]

            if log_type == "block":
                blockuser = re.sub(r"^[^:]+:(.+)$", "\\1", title)

                user_type = M.user_type(blockuser)
                if (type(user_type) != User
                        and user_type.start != user_type.end):
                    blockwiki = wiki
                else:
                    blockwiki = "global"

                if log_action == "block" or log_action == "reblock":
                    if (wiki in blockblacklistwiki
                        and re.search(
                            blockreasonblacklist, comment,
                            re.IGNORECASE) is not None):
                        reason = "於" + wiki + "封禁：" + comment
                        M.addblack_user(
                            blockuser, change["timestamp"], reason,
                            msgprefix="自動", wiki=blockwiki)
                        if change["log_params"]["duration"] in ["infinite", "indefinite", "never"]:
                            point = 365
                        else:
                            try:
                                endtime = strtotime(change["log_params"]["duration"])
                                duration = endtime - time()
                                point = max(int(duration / 86400) * 2, 14) + 10
                                if log_action == "reblock":
                                    oldpoint = M.getuser_score(M.user_type(blockuser))
                                    if point < oldpoint:
                                        point = 0
                                    else:
                                        point -= oldpoint
                            except Exception as e:
                                traceback.print_exc()
                                M.error(traceback.format_exc())
                                point = 30
                        M.adduser_score(M.user_type(blockuser), point, "autoblacklist/block")

            elif log_type == "protect":
                if log_action == "protect" or log_action == "modify":
                    if (wiki in protectblacklistwiki
                        and re.search(
                            protectreasonblacklist, comment,
                            re.IGNORECASE) is not None):
                        expiry = change["log_params"]["details"][0]["expiry"]
                        if expiry != "infinity":
                            endtime = datetime.datetime.strptime(expiry, "%Y%m%d%H%M%S").timestamp()
                            duration = endtime - time()
                            point = max(int(duration / 86400) * 2, 14)
                            reason = "保護：" + comment
                            M.addblack_page(
                                title, endtime, reason,
                                point=point, msgprefix="自動", wiki=wiki)

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc())
