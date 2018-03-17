# Wikimedia RecentChange Monitor

## 指令集
| 監視本地 | 監視其他wiki | 監視全域 | 附加原因 | 功能 |
| ------------- | ------------- |
| /adduser<br>`user` | /adduser<br>`user`&#124;`wiki` | /adduser<br>`user`&#124;global | /adduser<br>`user`<br>`reason` | 監視`user`在`wiki`的編輯<br>`wiki`須使用資料庫名<br>可附加原因`reason` |
| N/A | N/A | /addwhiteuser<br>`user` | /addwhiteuser<br>`user`<br>`reason` | 永不監視`user`在全域的編輯<br>可附加原因`reason` |
| /deluser<br>`user` | /deluser<br>`user`&#124;`wiki` | /deluser<br>`user`&#124;global| N/A | 取消監視`user`在`wiki`的編輯 |
| /addpage<br>`page` | /addpage<br>`page`&#124;`wiki` | N/A |  /addpage<br>`page`<br>`reason` | 監視`wiki`上的`page`的編輯<br>可附加原因`reason` |
| /delpage<br>`page` | /delpage<br>`page`&#124;`wiki` | N/A | N/A | 取消監視`wiki`上的`page`的編輯 |

| 頻道指令 | 功能 |
| ------------- | ------------- |
| /setadmin | 設定管理員，需reply對象 |
| /deladmin | 取消設定管理員，需reply對象 |
| /status | 檢查伺服器狀態 |
