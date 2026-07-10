if (Java.available) {
    Java.perform(function () {
        const Base64 = Java.use("android.util.Base64");
        Base64.encodeToString.overload("[B", "int").implementation = function (bytes, flags) {
            const ret = this.encodeToString(bytes, flags);
            console.log("[Base64.encodeToString]", ret);
            return ret;
        };
        Base64.decode.overload("java.lang.String", "int").implementation = function (value, flags) {
            console.log("[Base64.decode]", value);
            return this.decode(value, flags);
        };
    });
}
