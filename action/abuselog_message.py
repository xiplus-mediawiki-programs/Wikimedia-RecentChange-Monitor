import time
import traceback

import dateutil

from abuselog_message_config import chats, token
from abuselog_message_function import afLogo, result
from Monitor import Monitor


def main(log):
    M = Monitor()
    M.token = token
    try:
        timestr = dateutil.parser.parse(log['timestamp'])
        timestamp = int(timestr.timestamp()) + 3600 * 8
        day = '一二三四五六日'

        detailtext = M.link_abuselog(log['id'])
        if 'revid' in log and log['revid'] != '':
            detailtext += ' | ' + M.link_diff(log['revid'])

        message = '{0}{1}：{2} ({3}) 在 {4} 執行操作 "{5}" 時觸發{6}。採取的行動：{7} ； 過濾器描述：{8}（{9}）'.format(
            afLogo(log['filter_id'], log['filter']),
            time.strftime('%Y年%m月%d日 ({}) %H:%M', time.gmtime(timestamp)).format(day[timestr.weekday()]),
            M.link_user(log['user']),
            M.link_all('User_talk:{0}'.format(log['user']), '對話'),
            M.link_page(log['title']),
            log['action'],
            M.link_abusefilter(log['filter_id']),
            result(log['result']),
            log['filter'],
            detailtext
        )

        for chat_id in chats:
            print(chat_id)
            if chats[chat_id](log):
                M.sendmessage(message, chat_id=chat_id, token=token)

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
