import re
import traceback

from message_config import affollowwiki, followwiki
from Monitor import Monitor


def main(change):
    M = Monitor()
    try:
        if change["bot"]:
            return

        M.change_wiki_and_domain(change['wiki'], change["meta"]["domain"])

        wiki = change["wiki"]
        ctype = change["type"]
        user = change["user"]
        blackuser = user + "|" + wiki
        title = change["title"]
        comment = change["comment"]

        issend = False
        isblackuser = False
        message_append = ""

        if wiki != M.defaultwiki:
            message_append += "(" + wiki + ")"

        rows = M.check_user_blacklist(user)
        if len(rows) != 0:
            issend = True
            isblackuser = True
            blackuser = user + "|" + rows[0][3]
            message_append += (
                "\n（黑名單：\u200b" + M.parse_wikicode(rows[0][0]) + "\u200b")
            if rows[0][2] != "" and rows[0][2] != user:
                message_append += "，\u200b" + rows[0][2] + "\u200b"
                blackuser = rows[0][2] + "|" + rows[0][3]
            message_append += "，" + M.formattimediff(rows[0][1]) + "，" + str(rows[0][4]) + "p）"

        rows = M.check_page_blacklist(title, wiki)
        if len(rows) != 0 and len(M.check_user_whitelist(user)) == 0:
            issend = True
            message_append += (
                "\n（監視：" + M.parse_wikicode(rows[0][0]) +
                ', ' + M.formattimediff(rows[0][1]) + "，" + str(rows[0][2]) + "p）")

        if wiki not in followwiki and not issend:
            return

        if ctype == "edit":
            message = (
                M.link_user(user) + '編輯' + M.link_page(title) + '（' +
                M.link_diff(change["revision"]["new"]) + '）')
            if issend:
                M.sendmessage(
                    message + message_append, blackuser, title + "|" + M.wiki)
            if isblackuser:
                M.adduser_score(M.user_type(M.parse_user(blackuser)[0]), -1, "message/checklist")

        elif ctype == "new":
            message = M.link_user(user) + '建立' + M.link_page(title)
            if issend:
                M.sendmessage(
                    message + message_append, blackuser, title + "|" + M.wiki)
            if isblackuser:
                M.adduser_score(M.user_type(M.parse_user(blackuser)[0]), -1, "message/checklist")

        elif ctype == "142":
            if (change["namespace"] == 2600
                    and re.search(r'commented on "(唯一|最后)?警告 ', comment)):
                message = "用戶警告訊息：" + M.link_page(title) + "，請確認是否添加黑名單"
                M.sendmessage(message)

        elif ctype == "log":
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

                blockname = {
                    "unblock": "解封",
                    "block": "封禁",
                    "reblock": "重新封禁"}

                message = (
                    M.link_user(user) + blockname[log_action] +
                    M.link_user(blockuser) + '（' +
                    M.parse_wikicode(change["log_action_comment"]) + '）')
                M.sendmessage(
                    message + message_append, blockuser + "|" + blockwiki)

            elif log_type == "protect":
                if log_action in ["protect", "modify"] and re.search(r"高风险模板|高風險模板", comment):
                    return

                protectname = {
                    "unprotect": "解除保護",
                    "move_prot": "移動保護",
                    "protect": "保護",
                    "modify": "變更保護"}

                message = (
                    M.link_user(user) + protectname[log_action] +
                    M.link_page(title) + '（' +
                    M.parse_wikicode(comment) + '）')
                if log_action in ["protect", "modify"]:
                    message += (
                        '（'
                        + M.parse_wikicode(change["log_params"]["description"])
                        + '）')

                M.sendmessage(
                    message + message_append,
                    page=title + "|" + M.wiki)

            elif log_type == "abusefilter":
                abusefiltername = {
                    "hit": "觸發",
                    "modify": "修改",
                    "create": "建立"}

                if log_action in ["modify", "create"]:
                    message = "{}{}{}（{}）".format(
                        M.link_user(user),
                        abusefiltername[log_action],
                        M.link_abusefilter(change["log_params"]["newId"]),
                        M.link_all("Special:Abusefilter/history/{}/diff/prev/{}".format(
                            change["log_params"]["newId"], change["log_params"]["historyId"]
                        ), "差異")
                    )

                    if wiki != M.wiki:
                        message += "(" + wiki + ")"

                    if wiki in affollowwiki:
                        M.sendmessage(message)

            elif log_type == "globalauth":
                if log_action == "setstatus":
                    message = "{}全域鎖定{}（{}）".format(
                        M.link_user(user), M.link_user(title[5:-7]), M.parse_wikicode(change["log_action_comment"])
                    )
                    if issend:
                        M.sendmessage(message + message_append)

            elif log_type == "gblblock":
                if log_action in ["gblock2", "modify"]:
                    message = "{}全域封禁{}（{}）".format(
                        M.link_user(user), M.link_user(title[5:-7]), M.parse_wikicode(change["log_action_comment"])
                    )
                    if issend:
                        M.sendmessage(message + message_append)

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
