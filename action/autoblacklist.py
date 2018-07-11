import traceback
import json
from Monitor import *
from autoblacklist_config import followwiki, blockblacklistwiki, blockreasonblacklist


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
                and re.match(r"^(層級|层级)[234]", comment)):
            reason = "被"+user+"警告："+comment
            M.addblack_user(
                title[10:], change["timestamp"], reason, msgprefix="自動")

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

    except Exception as e:
        traceback.print_exc()
        M.error(traceback.format_exc())
