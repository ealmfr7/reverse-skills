if (Java.available) {
    Java.perform(function () {
        const DexClassLoader = Java.use("dalvik.system.DexClassLoader");
        DexClassLoader.$init.implementation = function (dexPath, optimizedDirectory, librarySearchPath, parent) {
            console.log("[DexClassLoader]", dexPath, optimizedDirectory, librarySearchPath, parent);
            return this.$init(dexPath, optimizedDirectory, librarySearchPath, parent);
        };
    });
}
