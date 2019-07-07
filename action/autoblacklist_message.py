import re
import time
import traceback

from autoblacklist_message_config import affollowwiki, followwiki


def main(M, change):
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
                "\n（監視：" + M.parse_wikicode(rows[0][0])
                + ', ' + M.formattimediff(rows[0][1]) + "，" + str(rows[0][2]) + "p）")

        if wiki not in followwiki and not issend:
            return

        M.addRC_wiki(change)

        if ctype == "edit":
            comment = re.sub(r'/\*.*?\*/', '', comment)
            comment = re.sub(r'^\s+$', '', comment)
            message = '{0}編輯{1}（{2}）（\u200b{3}\u200b）'.format(
                M.link_user(user),
                M.link_page(title),
                M.link_diff(change['revision']['new']),
                M.parse_wikicode(comment),
            ).replace('（\u200b\u200b）', '')
            if issend:
                M.sendmessage(
                    message + message_append, blackuser, title + "|" + M.wiki)
            if isblackuser:
                M.adduser_score(M.user_type(M.parse_user(blackuser)[0]), -1)

        elif ctype == "new":
            message = '{0}建立{1}（\u200b{2}\u200b）'.format(
                M.link_user(user),
                M.link_page(title),
                M.parse_wikicode(comment),
            ).replace('（\u200b\u200b）', '')
            if issend:
                M.sendmessage(
                    message + message_append, blackuser, title + "|" + M.wiki)
            if isblackuser:
                M.adduser_score(M.user_type(M.parse_user(blackuser)[0]), -1)

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

                if log_action in ["block", "reblock"] and re.search(r"blocked proxy", comment):
                    pass
                else:
                    message = (
                        M.link_user(user) + blockname[log_action]
                        + M.link_user(blockuser) + '（'
                        + M.parse_wikicode(change["log_action_comment"]) + '）')
                    M.sendmessage(
                        message + message_append, blockuser + "|" + blockwiki)

                if log_action == 'block':
                    M.log('[message] search bot message for {} after {}'.format(
                        blockuser + "|" + wiki, int(time.time() - 3600 * 8)), logtype='message/markblock')
                    M.db_execute(
                        """SELECT `message_id`, `message` FROM `bot_message`
                        WHERE `user` = %s AND `timestamp` > %s ORDER BY `timestamp` DESC
                        LIMIT 10""",
                        (blockuser + "|" + wiki, int(time.time() - 3600 * 8))
                    )
                    rows = M.db_fetchall()
                    M.log('[message] find {} itmes'.format(len(rows)), logtype='message/markblock')
                    for row in rows:
                        newmessage = '(已封) ' + row[1]
                        M.log('[message] try to edit message {} from {} to {}'.format(
                            row[0], row[1], newmessage), logtype='message/markblock')
                        M.editmessage(row[0], newmessage)

            elif log_type == "protect":
                if log_action in ["protect", "modify"] and re.search(r"高风险模板|高風險模板|被永久封禁的用戶頁|被永久封禁的用户页", comment):
                    return

                protectname = {
                    "unprotect": "解除保護",
                    "move_prot": "移動保護",
                    "protect": "保護",
                    "modify": "變更保護"}

                message = (
                    M.link_user(user) + protectname[log_action]
                    + M.link_page(title) + '（'
                    + M.parse_wikicode(comment) + '）')
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
