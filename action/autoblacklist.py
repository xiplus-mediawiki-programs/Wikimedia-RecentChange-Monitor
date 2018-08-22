import traceback
import json
from Monitor import *
from autoblacklist_config import *
from strtotime import strtotime
from time import time


def main(change):
    M = Monitor()
    try:
        M.change_wiki_and_domain(change['wiki'], change["meta"]["domain"])

        wiki = change["wiki"]
        ctype = change["type"]
        user = change["user"]
        blackuser = user+"|"+wiki
        title = change["title"]
        comment = change["comment"]

        if wiki not in followwiki:
            return

        if (ctype in ["edit", "new"]
                and change["namespace"] == 3
                and re.match(r"^User talk:", title)
                and re.match(r"^(層級|层级)[1234]", comment)
                and not re.search(warnreasonblacklist, comment)
                and user not in warnuserblacklist):
            reason = "被"+user+"警告："+comment
            M.addblack_user(
                title[10:], change["timestamp"], reason, msgprefix="自動")
            point = 5
            if re.match(r"^(層級|层级)2", comment):
                point = 10
            elif re.match(r"^(層級|层级)3", comment):
                point = 15
            elif re.match(r"^(層級|层级)4", comment):
                point = 20
            M.adduser_score(M.user_type(title[10:]), point)

        if ctype == "log":
            log_type = change["log_type"]
            log_action = change["log_action"]

            if log_type == "block":
                blockuser = title[5:]

                user_type = M.user_type(blockuser)
                if (type(user_type) != User
                        and user_type.start != user_type.end):
                    blockwiki = wiki
                else:
                    blockwiki = "global"

                if log_action == "block" or log_action == "reblock":
                    if (wiki in blockblacklistwiki
                        and re.search(
                            blockreasonblacklist, change["comment"],
                            re.IGNORECASE) is not None):
                        reason = "於"+wiki+"封禁："+change["comment"]
                        M.addblack_user(
                            blockuser, change["timestamp"], reason,
                            msgprefix="自動", wiki=blockwiki)
                        if change["log_params"]["duration"] in ["infinite", "indefinite", "never"]:
                            point = 365
                        else:
                            try:
                                endtime = strtotime(change["log_params"]["duration"])
                                duration = endtime-time()
                                point = int(duration/86400)+30
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
                        M.adduser_score(M.user_type(blockuser), point)

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc())
