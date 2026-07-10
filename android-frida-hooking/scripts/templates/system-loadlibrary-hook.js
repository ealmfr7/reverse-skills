if (Java.available) {
    Java.perform(function () {
        const System = Java.use("java.lang.System");
        System.loadLibrary.implementation = function (name) {
            console.log("[System.loadLibrary]", name);
            return this.loadLibrary(name);
        };
        System.load.overload("java.lang.String").implementation = function (path) {
            console.log("[System.load]", path);
            return this.load(path);
        };
    });
}
