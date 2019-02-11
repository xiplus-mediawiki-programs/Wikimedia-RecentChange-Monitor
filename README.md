# Wikimedia RecentChange Monitor

## 指令集
| 監視用戶 | 功能 |
| ---- | ---- |
| /adduser [-w 站點] [-r 原因] [-p 點數] username [reason] | 監視`username`在`w`的編輯<br>`username`可使用單一IP地址、CIDR、IP區段<br>`w`須使用[資料庫名](https://quarry.wmflabs.org/query/278)(不含_p)<br>可附加原因`reason` |
| /deluser [-w 站點] [username] [reason] | 取消監視`username`在`w`的編輯 |
| /addwhiteuser [-r 原因] username [reason] | 永不監視`username`在全域的編輯<br>可附加原因`reason` |
| /delwhiteuser username [reason] | 移除`username`白名單 |
| /checkuser [-w 站點] [username] | 列出`username`在`w`的監視狀態 |
| /setwiki [-u 用戶名] 站點 | 更改`u`的wiki |

| 監視頁面 | 功能 |
| ---- | ---- |
| /addpage [-w 站點] [-r 原因] [-p 點數] pagetitle [reason] | 監視`w`上的`pagetitle`的編輯<br>可附加原因`reason` |
| /massaddpage [-w 站點] [-r 原因] [-p 點數] pagetitle [pagetitle ...] | 大量監視頁面<br>可附加原因`r` |
| /delpage [-w 站點] [pagetitle] [reason] | 取消監視`w`上的`pagetitle`的編輯 |
| /checkpage [-w 站點] [pagetitle] | 列出`pagetitle`的監視狀態 |

| 頻道指令 | 功能 |
| ------------- | ------------- |
| /setadmin [nickname] | 設定管理員，需reply對象<br>可選設定別名`nickname`<br>管理員可更改自己的別名 |
| /deladmin | 取消設定管理員，需reply對象<br>管理員不可取消自己 |
| /status | 檢查伺服器狀態 |
