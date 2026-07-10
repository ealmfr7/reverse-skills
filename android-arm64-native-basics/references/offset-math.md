# Offset Math

Android `.so` files are usually PIE. Runtime addresses change each launch, but
module-relative offsets stay stable for the same binary.

## Formula

```text
offset = static_entry - image_base
runtime_address = frida_module_base + offset
```

Use:

```bash
python3 android-arm64-native-basics/scripts/offset-math.py \
  --image-base 0x100000 \
  --entry 0x101234 \
  --module-base 0x7a00000000
```

Frida:

```javascript
const module = Process.getModuleByName("libtarget.so");
const fn = module.base.add(0x1234);
```

## Common Mistakes

- Confusing file offset with virtual address.
- Using a rebased IDA/Ghidra address directly as a Frida runtime address.
- Using offsets from a different ABI or app version.
- Forgetting ASLR changes module base every run.
