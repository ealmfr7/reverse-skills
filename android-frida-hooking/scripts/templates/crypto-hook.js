if (Java.available) {
    Java.perform(function () {
        function bytesToHex(bytes) {
            if (!bytes) return "null";
            const out = [];
            for (let i = 0; i < bytes.length; i++) {
                out.push(("0" + (bytes[i] & 0xff).toString(16)).slice(-2));
            }
            return out.join("");
        }

        const Cipher = Java.use("javax.crypto.Cipher");
        Cipher.getInstance.overload("java.lang.String").implementation = function (transformation) {
            console.log("[Cipher] getInstance:", transformation);
            return this.getInstance(transformation);
        };

        Cipher.doFinal.overload("[B").implementation = function (input) {
            console.log("[Cipher] doFinal in:", bytesToHex(input));
            const ret = this.doFinal(input);
            console.log("[Cipher] doFinal out:", bytesToHex(ret));
            return ret;
        };

        const MessageDigest = Java.use("java.security.MessageDigest");
        MessageDigest.getInstance.overload("java.lang.String").implementation = function (algorithm) {
            console.log("[MessageDigest] getInstance:", algorithm);
            return this.getInstance(algorithm);
        };
    });
}
