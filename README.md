# Wikimedia RecentChange Monitor

## 指令集
| 監視本地 | 監視其他wiki | 監視全域 | 附加原因 | 功能 |
| ---- | ---- | ---- | ---- | ---- |
| /adduser<br>`user` | /adduser<br>`user`&#124;`wiki` | /adduser<br>`user`&#124;global | /adduser<br>`user`<br>`reason` | 監視`user`在`wiki`的編輯<br>`user`可使用單一IP地址、CIDR、IP區段<br>`wiki`須使用[資料庫名](https://quarry.wmflabs.org/query/278)(不含_p)<br>可附加原因`reason` |
| /deluser<br>`user` | /deluser<br>`user`&#124;`wiki` | /deluser<br>`user`&#124;global| N/A | 取消監視`user`在`wiki`的編輯 |
| N/A | N/A | /addwhiteuser<br>`user` | /addwhiteuser<br>`user`<br>`reason` | 永不監視`user`在全域的編輯<br>可附加原因`reason` |
| N/A | N/A | /delwhiteuser<br>`user` | N/A | 移除白名單 |
| /checkuser<br>`user` | /checkuser<br>`user`&#124;`wiki` | /checkuser<br>`user`&#124;global| N/A | 列出`user`的監視狀態 |
| /addpage<br>`page` | /addpage<br>`page`&#124;`wiki` | N/A |  /addpage<br>`page`<br>`reason` | 監視`wiki`上的`page`的編輯<br>可附加原因`reason` |
| /massaddpage<br>`page1`<br>`page2`<br>`reason` | /massaddpage<br>`page1`&#124;`wiki`<br>`page2`&#124;`wiki`<br>`reason` | N/A |  /massaddpage<br>`page1`<br>`page2`<br>`reason` | 大量監視頁面<br>**必須**附加原因`reason` |
| /delpage<br>`page` | /delpage<br>`page`&#124;`wiki` | N/A | N/A | 取消監視`wiki`上的`page`的編輯 |
| /checkpage<br>`page` | /checkpage<br>`page`&#124;`wiki` | N/A | N/A | 列出`page`的監視狀態 |

| 頻道指令 | 功能 |
| ------------- | ------------- |
| /setadmin<br>`name` | 設定管理員，需reply對象<br>可選設定別名`name`<br>管理員可更改自己的別名 |
| /deladmin | 取消設定管理員，需reply對象<br>管理員不可取消自己 |
| /status | 檢查伺服器狀態 |
