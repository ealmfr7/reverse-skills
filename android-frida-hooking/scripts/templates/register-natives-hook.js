// Logs JNI RegisterNatives calls on Android ART.
const candidates = [
    "_ZN3art3JNI15RegisterNativesEP7_JNIEnvP7_jclassPK15JNINativeMethodi",
    "RegisterNatives"
];

function findRegisterNatives() {
    for (const name of candidates) {
        const ptr = Module.findGlobalExportByName(name);
        if (ptr) return ptr;
    }

    for (const mod of Process.enumerateModules()) {
        if (mod.name.indexOf("libart.so") === -1) continue;
        for (const exp of mod.enumerateExports()) {
            if (exp.name.indexOf("RegisterNatives") !== -1) {
                return exp.address;
            }
        }
    }
    return null;
}

const registerNatives = findRegisterNatives();
if (!registerNatives) {
    console.log("[-] RegisterNatives not found");
} else {
    console.log("[+] RegisterNatives:", registerNatives);
    Interceptor.attach(registerNatives, {
        onEnter(args) {
            const env = args[0];
            const clazz = args[1];
            const methods = args[2];
            const count = args[3].toInt32();

            console.log("[JNI] RegisterNatives count:", count, "clazz:", clazz, "env:", env);

            const pointerSize = Process.pointerSize;
            for (let i = 0; i < count; i++) {
                const entry = methods.add(i * pointerSize * 3);
                const name = entry.readPointer().readCString();
                const sig = entry.add(pointerSize).readPointer().readCString();
                const fnPtr = entry.add(pointerSize * 2).readPointer();
                console.log("    " + name + " " + sig + " -> " + fnPtr);
            }
        }
    });
}
