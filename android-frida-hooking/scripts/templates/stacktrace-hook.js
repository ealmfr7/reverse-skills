if (Java.available) {
    Java.perform(function () {
        const Exception = Java.use("java.lang.Exception");
        const Log = Java.use("android.util.Log");
        console.log(Log.getStackTraceString(Exception.$new()));
    });
}
