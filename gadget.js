javascript:
(function(){

mw.loader.using(['mediawiki.util']).done(function(){

function gettoken() {
	if ($.cookie("cvn-smart-token") === null) {
		var token = prompt("尚未輸入token。請輸入：");
		if (token) {
			$.cookie("cvn-smart-token", token,  {path: '/'});
			return token;
		} else {
			return null;
		}
	}
	return $.cookie("cvn-smart-token");
}

function requestpage(type, askreason=true) {
	var token = gettoken();
	if (token) {
		var reason = "";
		if (askreason) {
			reason = prompt("原因：");
			if (reason === null) {
				return;
			}
		} else if (!confirm("確定移除監視？")) {
			return;
		}
		$.ajax({
			type: 'POST',
			url: 'https://xiplus.ddns.net/wikipedia_rc/api',
			data: {
				'action': type,
				'page': mw.config.get('wgPageName')+"|"+mw.config.get('wgDBname'),
				'reason': reason,
				'token': token
			},
			success: function success(data) {
				data = JSON.parse(data);
				mw.notify(["<pre>"+data.result+"</pre>"]);
			},
			error: function error(e) {
				console.log(data);
				mw.notify(["傳送請求時發生錯誤"]);
			}
		});
	} else {
		mw.notify(["動作已取消"]);
	}
}

function requestuser(type, askreason=true) {
	var token = gettoken();
	if (token) {
		var reason = "";
		if (askreason) {
			reason = prompt("原因：");
			if (reason === null) {
				return;
			}
		} else if (!confirm("確定移除黑名單？")) {
			return;
		}
		$.ajax({
			type: 'POST',
			url: 'https://xiplus.ddns.net/wikipedia_rc/api',
			data: {
				'action': type,
				'user': mw.config.get('wgRelevantUserName')+"|"+mw.config.get('wgDBname'),
				'reason': reason,
				'token': token
			},
			success: function success(data) {
				data = JSON.parse(data);
				mw.notify(["<pre>"+data.result+"</pre>"]);
			},
			error: function error(e) {
				console.log(data);
				mw.notify(["傳送請求時發生錯誤"]);
			}
		});
	} else {
		mw.notify(["動作已取消"]);
	}
}

if (mw.config.get('wgCanonicalSpecialPageName') === false) {
	var addpage = mw.util.addPortletLink(
		'p-cactions',
		'#',
		'cvn-smart: addpage'
	);
	$(addpage).on('click', function(){
		if (mw.config.get('wgArticleId') === 0 && !confirm("頁面不存在，確定要加入嗎？")) {
			return;
		}
		requestpage("addpage");
	});

	var delpage = mw.util.addPortletLink(
		'p-cactions',
		'#',
		'cvn-smart: delpage'
	);
	$(delpage).on('click', function(){
		requestpage("delpage", false);
	});
}

if (mw.config.get('wgRelevantUserName') !== null) {
	var adduser = mw.util.addPortletLink(
		'p-cactions',
		'#',
		'cvn-smart: adduser'
	);
	$(adduser).on('click', function(){
		requestuser("adduser");
	});

	var deluser = mw.util.addPortletLink(
		'p-cactions',
		'#',
		'cvn-smart: deluser'
	);
	$(deluser).on('click', function(){
		requestuser("deluser", false);
	});
}

});

})();
