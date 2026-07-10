if (Java.available) {
    Java.perform(function () {
        const FileInputStream = Java.use("java.io.FileInputStream");
        FileInputStream.$init.overload("java.lang.String").implementation = function (path) {
            console.log("[FileInputStream]", path);
            return this.$init(path);
        };

        const FileOutputStream = Java.use("java.io.FileOutputStream");
        FileOutputStream.$init.overload("java.lang.String").implementation = function (path) {
            console.log("[FileOutputStream]", path);
            return this.$init(path);
        };
    });
}
