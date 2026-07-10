if (Java.available) {
    Java.perform(function () {
        const SharedPreferencesImpl = Java.use("android.app.SharedPreferencesImpl");

        SharedPreferencesImpl.getString.implementation = function (key, defValue) {
            const ret = this.getString(key, defValue);
            console.log("[SharedPreferences] getString", key, "=>", ret);
            return ret;
        };

        const EditorImpl = Java.use("android.app.SharedPreferencesImpl$EditorImpl");
        EditorImpl.putString.implementation = function (key, value) {
            console.log("[SharedPreferences] putString", key, "=", value);
            return this.putString(key, value);
        };
    });
}
