import datetime
import re
import time
import traceback

from message_config import messagewiki, chats, token
from message_function import block_flags, protect_description, parse_rights


def main(M, change):
    try:
        if change['type'] == 'abuselog':
            return

        day = '一二三四五六日'
        timestr = time.strftime('%Y年%m月%d日 ({}) %H:%M', time.gmtime(change['timestamp'] + 3600 * 8)).format(
            day[datetime.datetime.fromtimestamp(change['timestamp']).weekday()])

        wiki = change['wiki']

        if wiki not in messagewiki:
            return

        M.change_wiki_and_domain(change['wiki'], change['meta']['domain'])

        ctype = change['type']

        message = ''

        if ctype == 'log':
            log_type = change['log_type']
            log_action = change['log_action']

            if log_type == 'block':
                target = re.sub(r"^[^:]+:(.+)$", "\\1", change['title'])

                if log_action == 'block':
                    message = '#封禁 {0} {1}已封鎖{2}期限為{3}（{4}）（{5}）'.format(
                        timestr,
                        M.link_user(change['user']),
                        M.link_user(target),
                        change['log_params']['duration'],
                        block_flags(change['log_params']['flags']),
                        M.parse_wikicode(change['comment']),
                    ).replace('（）', '')

                elif log_action == 'reblock':
                    message = '#封禁 {0} {1}已變更{2}的封鎖設定期限為{3}（{4}）（{5}）'.format(
                        timestr,
                        M.link_user(change['user']),
                        M.link_user(target),
                        change['log_params']['duration'],
                        block_flags(change['log_params']['flags']),
                        M.parse_wikicode(change['comment']),
                    ).replace('（）', '')

                elif log_action == 'unblock':
                    message = '#封禁 {0} {1}已解除封鎖{2}（{3}）'.format(
                        timestr,
                        M.link_user(change['user']),
                        M.link_user(target),
                        M.parse_wikicode(change['comment']),
                    ).replace('（）', '')

            elif log_type == 'protect':
                if log_action == 'protect':
                    message = '#保護 {0} {1}已保護{2}{3}（{4}）'.format(
                        timestr,
                        M.link_user(change['user']),
                        M.link_page(change['title']),
                        protect_description(change['log_params']['description']),
                        M.parse_wikicode(change['comment']),
                    ).replace('（）', '')

                elif log_action == 'modify':
                    message = '#保護 {0} {1}已更改{2}的保護層級{3}（{4}）'.format(
                        timestr,
                        M.link_user(change['user']),
                        M.link_page(change['title']),
                        protect_description(change['log_params']['description']),
                        M.parse_wikicode(change['comment']),
                    ).replace('（）', '')

                elif log_action == 'move_prot':
                    pass

                elif log_action == 'unprotect':
                    message = '#保護 {0} {1}已移除{2}的保護（{3}）'.format(
                        timestr,
                        M.link_user(change['user']),
                        M.link_page(change['title']),
                        M.parse_wikicode(change['comment']),
                    ).replace('（）', '')

            elif log_type == 'newusers':
                target = re.sub(r"^[^:]+:(.+)$", "\\1", change['title'])

                auto = ''
                if log_action == '':
                    auto = '自動'
                email = ''
                if log_action == 'byemail':
                    email = '並且以電子郵件通知密碼'

                message = '#新用戶 {0} {1}已{4}建立使用者帳號{2}{5}（{3}）'.format(
                    timestr,
                    M.link_user(change['user']) if change['user'] != target else '',
                    M.link_user(target),
                    M.parse_wikicode(change['comment']),
                    auto,
                    email,
                ).replace('（）', '')

            elif log_type == 'rights':
                target = re.sub(r"^[^:]+:(.+)$", "\\1", change['title'])

                message = '#權限 {0} {1}已更改{2}的群組成員資格由{3}成為{4}（{5}）'.format(
                    timestr,
                    M.link_user(change['user']),
                    M.link_user(target),
                    parse_rights(change['log_params']['oldgroups'], change['log_params']['oldmetadata']),
                    parse_rights(change['log_params']['newgroups'], change['log_params']['newmetadata']),
                    M.parse_wikicode(change['comment']),
                ).replace('（）', '')

            elif log_type == 'delete':
                if log_action == 'delete':
                    message = '#刪除 {0} {1}刪除頁面{2}（{3}）'.format(
                        timestr,
                        M.link_user(change['user']),
                        M.link_page(change['title']),
                        M.parse_wikicode(change['comment']),
                    ).replace('（）', '')

                elif log_action == 'delete_redir':
                    pass

                elif log_action == 'restore':
                    message = '#刪除 {0} {1}還原頁面{2}（{3}）'.format(
                        timestr,
                        M.link_user(change['user']),
                        M.link_page(change['title']),
                        M.parse_wikicode(change['comment']),
                    ).replace('（）', '')

                elif log_action == 'revision':
                    pass

        if message:
            for chat_id in chats:
                if chats[chat_id](change):
                    M.sendmessage(message, chat_id=chat_id, token=token)

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
