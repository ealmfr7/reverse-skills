// Replace TARGET_CLASS and overload signature before running.
if (Java.available) {
    Java.perform(function () {
        const Target = Java.use("com.example.TARGET_CLASS");

        Target.$init.overloads.forEach(function (overload) {
            const sig = overload.argumentTypes.map(t => t.className).join(", ");
            console.log("[+] constructor overload:", "TARGET_CLASS(" + sig + ")");

            overload.implementation = function () {
                console.log("[+] constructor called:", sig);
                for (let i = 0; i < arguments.length; i++) {
                    console.log("    arg" + i + ":", arguments[i]);
                }
                return overload.apply(this, arguments);
            };
        });
    });
}
