import datetime
import re
import traceback
from time import time

from autoblacklist_config import (blockblacklistwiki, blockreasonblacklist,
                                  followwiki, protectblacklistwiki,
                                  protectreasonblacklist, warnreasonblacklist,
                                  warnuserblacklist)
from strtotime import strtotime


# https://gerrit.wikimedia.org/g/mediawiki/core/+/5ddbe251acee87b6633c30c859c73ec391a35530/includes/GlobalFunctions.php#2950
INFINITY_ALIASES = ['infinite', 'indefinite', 'infinity', 'never']


def main(M, change):
    try:
        if change['type'] == 'abuselog':
            return

        M.change_wiki_and_domain(change['wiki'], change["meta"]["domain"])

        wiki = change["wiki"]
        ctype = change["type"]
        user = change["user"]
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
            if user == target:
                # No self-warning
                return
            point = 0
            if re.match(r"^(層級|层级)1", comment):
                point = 5
            elif re.match(r"^(層級|层级)2", comment):
                point = 10
            elif re.match(r"^(層級|层级)3", comment):
                point = 15
            elif re.match(r"^(層級|层级)4", comment):
                point = 20
            elif re.match(r"^(單層級通知|单层级通知)", comment):
                point = 10
            elif re.match(r"^(單層級警告|单层级警告)", comment):
                point = 10
            if point > 0:
                M.addblack_user(
                    target, change["timestamp"], reason, msgprefix="自動")
                M.adduser_score(M.user_type(target), point)

                page = re.search(r"(?:于|於)\[\[:?([^\]]+?)]]", comment)
                if page:
                    pagename = page.group(1)
                    if not re.match(r"^((Wikipedia|Help|User)([ _]talk)?|Special|UT?):", pagename, flags=re.I):
                        reason = target + "編輯但被警告：" + comment
                        M.addblack_page(
                            pagename, time(), reason,
                            point=3, msgprefix="自動", wiki=wiki)

        if ctype == "log":
            log_type = change["log_type"]
            log_action = change["log_action"]

            if log_type == "block":
                blockuser = re.sub(r"^[^:]+:(.+)$", "\\1", title)

                user_type = M.user_type(blockuser)
                if (not user_type.isuser
                        and user_type.start != user_type.end):
                    blockwiki = wiki
                else:
                    blockwiki = "global"

                if log_action in ["block", "reblock"]:
                    if (wiki in blockblacklistwiki
                        and re.search(
                            blockreasonblacklist, comment,
                            re.IGNORECASE) is not None):
                        reason = "於" + wiki + "封禁：" + comment
                        M.addblack_user(
                            blockuser, change["timestamp"], reason,
                            msgprefix="自動", wiki=blockwiki)
                        if change['log_params']['duration'] in INFINITY_ALIASES:
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
                            except Exception:
                                traceback.print_exc()
                                M.error(traceback.format_exc())
                                point = 30
                        M.adduser_score(M.user_type(blockuser), point)

            elif log_type == "protect":
                if log_action in ["protect", "modify"]:
                    if (wiki in protectblacklistwiki
                        and re.search(
                            protectreasonblacklist, comment,
                            re.IGNORECASE) is not None):
                        expiry = change["log_params"]["details"][0]["expiry"]
                        if expiry not in INFINITY_ALIASES:
                            endtime = datetime.datetime.strptime(expiry, "%Y%m%d%H%M%S").timestamp()
                            duration = endtime - time()
                            point = max(int(duration / 86400) * 2, 14)
                            reason = "保護：" + comment
                            M.addblack_page(
                                title, endtime, reason,
                                point=point, msgprefix="自動", wiki=wiki)

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
