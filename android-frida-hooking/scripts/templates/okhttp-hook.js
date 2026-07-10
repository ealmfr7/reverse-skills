// Observes OkHttp requests. Keep response body hooks disabled unless needed.
if (Java.available) {
    Java.perform(function () {
        try {
            const RequestBuilder = Java.use("okhttp3.Request$Builder");
            RequestBuilder.url.overload("java.lang.String").implementation = function (url) {
                console.log("[OkHttp] url:", url);
                return this.url(url);
            };
            RequestBuilder.header.implementation = function (name, value) {
                console.log("[OkHttp] header:", name, "=", value);
                return this.header(name, value);
            };
        } catch (e) {
            console.log("[-] OkHttp Request$Builder hook failed:", e);
        }

        try {
            const OkHttpClient = Java.use("okhttp3.OkHttpClient");
            OkHttpClient.newCall.implementation = function (request) {
                console.log("[OkHttp] newCall:", request.method(), String(request.url()));
                return this.newCall(request);
            };
        } catch (e) {
            console.log("[-] OkHttpClient hook failed:", e);
        }
    });
}
