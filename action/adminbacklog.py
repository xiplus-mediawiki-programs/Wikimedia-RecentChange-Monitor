import json
import logging
import socket
import subprocess
import traceback
from adminbacklog_config import adminbacklog, epstatus


def speedy_deletion(csd, pagename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('localhost', 1234))

    data = {
        'csd': csd,
        'page': pagename
    }
    data = json.dumps(data)
    data = data.encode()
    sock.send(data)
    sock.close()


def main(M, change):
    try:
        wiki = change['wiki']
        if wiki not in ['zhwiki', 'metawiki']:
            return

        M.change_wiki_and_domain(change['wiki'], change['meta']['domain'])

        ctype = change['type']

        if ctype == 'edit':
            if change['title'] == 'Wikipedia:防滥用过滤器/错误报告':
                subprocess.Popen(['php', adminbacklog, '-r', 'affp'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run affp')

            elif change['title'] == 'Wikipedia:存廢覆核請求':
                subprocess.Popen(['php', adminbacklog, '-r', 'drv'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run drv')

            elif change['title'] == 'Wikipedia:更改用户名':
                subprocess.Popen(['php', adminbacklog, '-r', 'uc'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run uc')

            # elif change['title'] == 'Wikipedia:頁面存廢討論/積壓討論':
            #     subprocess.Popen(['php', adminbacklog, '-r', 'afdb'],
            #                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            #     lo.info('run afdb')

            elif change['title'] == 'Wikipedia:当前的破坏':
                subprocess.Popen(['php', adminbacklog, '-r', 'vip'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run vip')

            # elif change['title'] == 'Wikipedia:管理员通告板/3RR':
            #     subprocess.Popen(['php', adminbacklog, '-r', 'ewip'],
            #                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            #     lo.info('run ewip')

            elif change['title'] == 'Wikipedia:需要管理員注意的用戶名':
                subprocess.Popen(['php', adminbacklog, '-r', 'uaa'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run uaa')

            elif change['title'] == 'Wikipedia:请求保护页面':
                subprocess.Popen(['php', adminbacklog, '-r', 'rfpp'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run rfpp')

            # elif change['title'] == 'Wikipedia:元維基用戶查核協助請求':
            #     subprocess.Popen(['php', adminbacklog, '-r', 'rfcuham'],
            #                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            #     lo.info('run rfcuham')

            # elif change['title'] == 'Steward requests/Checkuser':
            #     subprocess.Popen(['php', adminbacklog, '-r', 'rfcu'],
            #                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            #     lo.info('run rfcu')

            elif change['title'] == 'Wikipedia:申请解除权限':
                subprocess.Popen(['php', adminbacklog, '-r', 'revoke'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run revoke')

            elif change['title'] == 'Wikipedia:權限申請/申請巡查權':
                subprocess.Popen(['php', adminbacklog, '-r', 'rfrpatrol'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run rfrpatrol')

            elif change['title'] == 'Wikipedia:權限申請/申請回退權':
                subprocess.Popen(['php', adminbacklog, '-r', 'rfrrollback'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run rfrrollback')

            elif change['title'] == 'Wikipedia:權限申請/申請IP封禁例外權':
                subprocess.Popen(['php', adminbacklog, '-r', 'rfripbe'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run rfripbe')

            elif change['title'] == 'Wikipedia:權限申請/申請巡查豁免權':
                subprocess.Popen(['php', adminbacklog, '-r', 'rfrautoreview'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run rfrautoreview')

            elif change['title'] == 'Wikipedia:權限申請/申請確認用戶權':
                subprocess.Popen(['php', adminbacklog, '-r', 'rfrconfirm'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run rfrconfirm')

            elif change['title'] == 'Wikipedia:權限申請/申請大量訊息發送權':
                subprocess.Popen(['php', adminbacklog, '-r', 'rfrmms'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run rfrmms')

            elif change['title'] == 'Wikipedia:權限申請/申請跨維基導入權':
                subprocess.Popen(['php', adminbacklog, '-r', 'rfrtranswiki'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run rfrtranswiki')

            elif change['title'] == 'Wikipedia:權限申請/申請模板編輯權':
                subprocess.Popen(['php', adminbacklog, '-r', 'rftpe'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run rftpe')

            elif change['title'] == 'Wikipedia talk:AutoWikiBrowser/CheckPage':
                subprocess.Popen(['php', adminbacklog, '-r', 'rfrawb'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run rfrawb')

            elif change['title'] == 'Wikipedia:机器用户/申请':
                subprocess.Popen(['php', adminbacklog, '-r', 'rfrflood'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run rfrflood')

            elif change['title'] == 'Wikipedia:修订版本删除请求':
                subprocess.Popen(['php', adminbacklog, '-r', 'rrd'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run rrd')

            elif change['title'] == 'Wikipedia:頁面存廢討論/疑似侵權':
                subprocess.Popen(['php', adminbacklog, '-r', 'cv'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run cv')

        elif ctype == 'new':
            if wiki == 'zhwiki' and change['length']['new'] < 100:
                speedy_deletion('G15-3', change['title'])
            if wiki == 'zhwiki' and change['namespace'] % 2 == 1:
                speedy_deletion('G15-4', change['title'])

        elif ctype == 'categorize':
            if change['title'] == 'Category:快速删除候选':
                subprocess.Popen(['php', adminbacklog, '-r', 'csd'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run csd')

            elif change['title'] == 'Category:維基百科編輯全保護頁面請求':
                subprocess.Popen(['php', adminbacklog, '-r', 'epfull'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run epfull')

            elif change['title'] == 'Category:維基百科編輯模板保護頁面請求':
                subprocess.Popen(['php', adminbacklog, '-r', 'eptemp'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run eptemp')

            elif change['title'] == 'Category:維基百科編輯半保護頁面請求':
                subprocess.Popen(['php', adminbacklog, '-r', 'epsemi'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run epsemi')

            elif change['title'] == 'Category:維基百科編輯無保護頁面請求':
                subprocess.Popen(['php', adminbacklog, '-r', 'epnone'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run epnone')

            # elif change['title'] == 'Category:移動請求':
            #     subprocess.Popen(['php', adminbacklog, '-r', 'rm'],
            #                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            #     lo.info('run rm')

            elif change['title'] == 'Category:封禁及禁制申诉':
                subprocess.Popen(['php', adminbacklog, '-r', 'unblock'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run unblock')

            elif change['title'] == 'Category:維基百科編輯被保護頁面請求':
                subprocess.Popen(['python3.6', epstatus],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logging.debug('run ep-status')

        elif ctype == 'log':
            log_type = change['log_type']
            log_action = change['log_action']

            if log_type == 'move':
                # M.log('[adminbacklog] {}'.format(json.dumps(change)))
                if wiki == 'zhwiki' and change['log_params']['noredir'] == '0' and change['namespace'] in [0, 118]:
                    speedy_deletion('R2', change['title'])
                    # cmd = 'sleep 60; python3.6 {} {}'.format(sdr2, shlex.quote())
                    # M.log('[adminbacklog] command {}'.format(cmd))
                    # subprocess.Popen(cmd, shell=True,
                    #   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            elif log_type == 'delete':
                if log_action == 'delete':
                    if wiki == 'zhwiki' and 'WP:CSD' in change['comment']:
                        subprocess.Popen(['php', adminbacklog, '-r', 'csd'],
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        logging.debug('run csd')

                    if wiki == 'zhwiki':
                        # cmd = 'sleep 60; python3.6 {} {}'.format(sdg153, shlex.quote(change['title']))
                        # M.log('[adminbacklog] command {}'.format(cmd))
                        # subprocess.Popen(cmd, shell=True,
                        #                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        speedy_deletion('G15-3', change['title'])

                        if change['namespace'] % 2 == 0:
                            speedy_deletion('G15-4', change['title'])
                            # cmd = 'sleep 60; python3.6 {} {}'.format(sdg154, shlex.quote(change['title']))
                            # M.log('[adminbacklog] command {}'.format(cmd))
                            # subprocess.Popen(cmd, shell=True,
                            #                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    except Exception:
        traceback.print_exc()
        M.error(traceback.format_exc())
