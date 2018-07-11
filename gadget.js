javascript:
(function(){

mw.loader.using(['mediawiki.util']).done(function(){

function gettoken() {
	if ($.cookie("cvn_smart_authorized") !== "1") {
		unauthorize();
		return null;
	}
	return $.cookie("cvn_smart_token");
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
				console.log(data);
				if (data.nopermission) {
					unauthorize();
					return;
				}
				mw.notify(["<pre>"+data.message+"</pre>"]);
			},
			error: function error(e) {
				console.log(e);
				mw.notify(["傳送請求時發生錯誤\n"+e.statusText]);
			}
		});
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
				console.log(data);
				if (data.nopermission) {
					unauthorize();
					return;
				}
				mw.notify(["<pre>"+data.message+"</pre>"]);
			},
			error: function error(e) {
				console.log(e);
				mw.notify(["傳送請求時發生錯誤\n"+e.statusText]);
			}
		});
	}
}

function authorize() {
	if ($.cookie("cvn_smart_authorized") === "1") {
		mw.notify(["您已經認證過了"]);
		return;
	}
	var token = prompt("輸入存取權杖：");
	if (token) {
		$.ajax({
			type: 'POST',
			url: 'https://xiplus.ddns.net/wikipedia_rc/api',
			data: {
				'action': 'authorize',
				'token': token
			},
			success: function success(data) {
				data = JSON.parse(data);
				if (data.result === "success") {
					mw.notify(["已成功認證，您是 "+data.user]);
					$.cookie("cvn_smart_authorized", "1", {path: "/"});
					$.cookie("cvn_smart_token", token, {path: "/"});
					showbutton();
				} else {
					mw.notify(["認證失敗，存取權杖錯誤或過期，請向機器人私訊 /gettoken 以獲得新權杖"]);
				}
			},
			error: function error(e) {
				console.log(e);
				mw.notify(["傳送請求時發生錯誤\n"+e.statusText]);
			}
		});
	} else {
		mw.notify(["動作已取消"]);
	}
}

function showbutton(){
	if (window.cvn_smart_button) {
		return;
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

	window.cvn_smart_button = true;
}

function unauthorize(first=false) {
	if (window.cvn_smart_authorize_button === undefined) {
		var authorizebtn = mw.util.addPortletLink(
			'p-cactions',
			'#',
			'cvn-smart: authorize'
		);
		$(authorizebtn).on('click', function(){
			authorize();
		});
		window.cvn_smart_authorize_button = true;
	}
	$.cookie("cvn_smart_authorized", "0", {path: "/"});
	$.cookie("cvn_smart_token", "", {path: "/"});
	if (first && $.cookie("cvn_smart_firstnotice")) {
		return;
	}
	mw.notify(["cvn-smart: 您尚未進行認證，或是存取權杖已過期"]);
	var date = new Date();
	date.setTime(date.getTime() + 1000 * 86400);
	$.cookie("cvn_smart_firstnotice", "1", {path: "/", expiry: date});
}


if ($.cookie("cvn_smart_authorized") === "1") {
	showbutton();
} else {
	unauthorize(true);
}

});

})();
