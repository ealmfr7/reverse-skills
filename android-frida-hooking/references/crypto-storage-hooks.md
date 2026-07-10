# Crypto and Storage Hooks

## Use Cases

Hook crypto/storage APIs to understand authorized app behavior:

- What data is stored locally?
- Which values are encrypted/decrypted at runtime?
- Which encoding or hashing API transforms a value?
- Where does a token or feature flag enter app logic?

## SharedPreferences

Use `scripts/templates/sharedprefs-hook.js` to observe reads and writes:

- `getString`
- `getBoolean`
- `getInt`
- `putString`
- `putBoolean`
- `apply`
- `commit`

Redact tokens before presenting logs.

## Base64

Base64 is encoding, not encryption. Hook it to reveal data movement:

```javascript
const Base64 = Java.use("android.util.Base64");
Base64.encodeToString.overload("[B", "int").implementation = function (bytes, flags) {
    const ret = this.encodeToString(bytes, flags);
    console.log("Base64.encodeToString ret:", ret);
    return ret;
};
```

## Java Crypto

High-value classes:

- `javax.crypto.Cipher`
- `javax.crypto.spec.SecretKeySpec`
- `javax.crypto.spec.IvParameterSpec`
- `java.security.MessageDigest`
- `javax.crypto.Mac`

Use `scripts/templates/crypto-hook.js`.

Use `scripts/templates/base64-hook.js` when the app appears to encode/decode
tokens, JSON blobs, or binary payloads through Android Base64 APIs.

Use `scripts/templates/file-io-hook.js` when the target behavior may read/write
tokens, configs, downloaded payloads, or local cache files.

## Safety

Treat keys, tokens, and decrypted personal data as sensitive. Keep logs minimal,
redacted, and tied to an authorized test account.
