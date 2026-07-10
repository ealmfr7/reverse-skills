// Replace libtarget.so and target_export before running.
function installNativeExportHook() {
    const mod = Process.getModuleByName("libtarget.so");
    const target = mod.getExportByName("target_export");

    Interceptor.attach(target, {
        onEnter(args) {
            console.log("[native] target_export called");
            console.log("    arg0:", args[0]);
            console.log("    arg1:", args[1]);
        },
        onLeave(retval) {
            console.log("    ret:", retval);
        }
    });

    console.log("[+] Native hook installed:", mod.name, target);
}

installNativeExportHook();
