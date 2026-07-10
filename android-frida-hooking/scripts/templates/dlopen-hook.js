// Replace libtarget.so and add target hooks inside installHooks().
function hookModuleLoad(moduleName, callback) {
    const dlopen = Module.findGlobalExportByName("android_dlopen_ext")
        || Module.findGlobalExportByName("dlopen");

    if (!dlopen) {
        throw new Error("dlopen/android_dlopen_ext not found");
    }

    const hooked = new Set();

    Interceptor.attach(dlopen, {
        onEnter(args) {
            this.path = args[0].isNull() ? null : args[0].readCString();
            this.shouldHook = this.path && this.path.indexOf(moduleName) !== -1;
        },
        onLeave(retval) {
            if (!this.shouldHook || retval.isNull()) return;

            const mod = Process.findModuleByName(moduleName);
            if (!mod) return;

            const key = mod.base.toString();
            if (hooked.has(key)) return;
            hooked.add(key);

            callback(mod);
        }
    });
}

function hookNowOrOnLoad(moduleName, callback) {
    const mod = Process.findModuleByName(moduleName);
    if (mod) {
        callback(mod);
        return;
    }
    hookModuleLoad(moduleName, callback);
}

hookNowOrOnLoad("libtarget.so", function installHooks(mod) {
    console.log("[+] Module ready:", mod.name, mod.base, mod.size);
    // const fn = mod.getExportByName("target_export");
    // Interceptor.attach(fn, { onEnter(args) {}, onLeave(retval) {} });
});
