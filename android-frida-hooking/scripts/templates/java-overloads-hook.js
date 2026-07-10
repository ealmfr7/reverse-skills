// Replace TARGET_CLASS and TARGET_METHOD before running.
if (Java.available) {
    Java.perform(function () {
        const Target = Java.use("com.example.TARGET_CLASS");
        const method = Target.TARGET_METHOD;

        method.overloads.forEach(function (overload) {
            const sig = overload.argumentTypes.map(t => t.className).join(", ");
            console.log("[+] overload:", "TARGET_METHOD(" + sig + ")");

            overload.implementation = function () {
                console.log("[+] TARGET_METHOD(" + sig + ") called");
                for (let i = 0; i < arguments.length; i++) {
                    console.log("    arg" + i + ":", arguments[i]);
                }
                const ret = overload.apply(this, arguments);
                console.log("    ret:", ret);
                return ret;
            };
        });
    });
}
