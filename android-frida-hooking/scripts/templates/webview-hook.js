if (Java.available) {
    Java.perform(function () {
        const WebView = Java.use("android.webkit.WebView");

        WebView.loadUrl.overload("java.lang.String").implementation = function (url) {
            console.log("[WebView] loadUrl:", url);
            return this.loadUrl(url);
        };

        WebView.evaluateJavascript.implementation = function (script, callback) {
            console.log("[WebView] evaluateJavascript:", script);
            return this.evaluateJavascript(script, callback);
        };

        WebView.addJavascriptInterface.implementation = function (obj, name) {
            console.log("[WebView] addJavascriptInterface:", name, obj);
            return this.addJavascriptInterface(obj, name);
        };
    });
}
