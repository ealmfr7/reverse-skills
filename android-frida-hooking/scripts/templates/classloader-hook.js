// Replace TARGET_CLASS. Use when Java.use() cannot resolve a class.
if (Java.available) {
    Java.perform(function () {
        const targetClass = "com.example.TARGET_CLASS";
        const Class = Java.use("java.lang.Class");

        Java.enumerateClassLoaders({
            onMatch(loader) {
                try {
                    Class.forName(targetClass, false, loader);
                    console.log("[+] Loader can resolve " + targetClass + ":", loader);
                    Java.classFactory.loader = loader;

                    const Target = Java.use(targetClass);
                    console.log("[+] Java.use succeeded:", Target);
                } catch (e) {
                    // Not this loader.
                }
            },
            onComplete() {
                console.log("[+] ClassLoader scan complete");
            }
        });
    });
}
