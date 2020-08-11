def block_flags(flags):
    f = {
        'anononly': '僅限匿名使用者',
        'noautoblock': '停用自動封鎖',
        'nocreate': '停用帳號建立',
        'noemail': '停用電子郵件',
        'nousertalk': '無法編輯自己的對話頁面'
    }
    for key in f:
        flags = flags.replace(key, f[key])
    flags = flags.replace(',', '、')
    return flags


def protect_description(description):
    r = {
        '[edit=': '[編輯=',
        '[move=': '[移動=',
        '[create=': '[建立=',
        '=autoconfirmed]': '=僅允許已自動確認的使用者]',
        '=sysop]': '=僅限管理員]',
        '=templateeditor]': '=僅允許模板編輯員和管理員]',
    }
    for key in r:
        description = description.replace(key, r[key])
    return description


rightname = {
    'accountcreator': '大量帳號建立者',
    'autoreviewer': '巡查豁免者',
    'bot': '機器人',
    'bureaucrat': '行政員',
    'confirmed': '已確認的使用者',
    'eventparticipant': '活動參與者',
    'filemover': '檔案移動員',
    'flood': '機器使用者',
    'import': '匯入者',
    'interface-admin': '介面管理員',
    'ipblock-exempt': 'IP 封鎖例外',
    'massmessage-sender': '大量訊息傳送者',
    'oversight': '監督員',
    'patroller': '巡查員',
    'rollbacker': '回退員',
    'sysop': '管理員',
    'templateeditor': '模板編輯員',
    'transwiki': '跨維基匯入者',
}


def parse_rights(groups, metadatas):
    if len(groups) == 0:
        return '無'
    if isinstance(groups, dict):
        groups = list(groups.values())
    res = []
    for group, metadata in zip(groups, metadatas):
        if 'expiry' in metadata:
            res.append('{}（{}/{}/{} {}:{}）'.format(
                rightname[group],
                metadata['expiry'][0:4],
                metadata['expiry'][4:6],
                metadata['expiry'][6:8],
                metadata['expiry'][8:10],
                metadata['expiry'][10:12],
            ))
        else:
            res.append(rightname[group])
    return '、'.join(res)
