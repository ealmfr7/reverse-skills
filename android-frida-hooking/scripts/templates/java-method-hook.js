// Replace TARGET_CLASS and TARGET_METHOD before running.
if (Java.available) {
    Java.perform(function () {
        const Target = Java.use("com.example.TARGET_CLASS");

        Target.TARGET_METHOD.implementation = function () {
            console.log("[+] TARGET_METHOD called");
            for (let i = 0; i < arguments.length; i++) {
                console.log("    arg" + i + ":", arguments[i]);
            }

            const ret = this.TARGET_METHOD.apply(this, arguments);
            console.log("    ret:", ret);
            return ret;
        };

        console.log("[+] Hook installed: com.example.TARGET_CLASS.TARGET_METHOD");
    });
}
