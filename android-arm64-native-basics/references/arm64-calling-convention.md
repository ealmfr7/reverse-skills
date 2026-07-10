# ARM64 Calling Convention

## Registers

| Register | Meaning |
|---|---|
| `x0`-`x7` | first eight integer/pointer arguments |
| `w0`-`w7` | lower 32-bit view of `x0`-`x7` |
| `x0` | return value |
| `x8` | indirect result location or syscall number depending context |
| `x29` | frame pointer |
| `x30` / `lr` | link register / return address |
| `sp` | stack pointer |

Floating-point arguments use `v0`-`v7` / `d0` / `s0` depending type.

## Practical Reading

- `bl sub_x`: function call; return address goes to `x30`.
- `ret`: return to `x30`.
- `ldr xN, [xM, #0x18]`: load a pointer/64-bit value from struct field offset
  `0x18`.
- `str wN, [xM, #0x10]`: store a 32-bit value into field offset `0x10`.
- `cbz x0, label`: branch if pointer/value is zero.
- `tbz w0, #n, label`: branch if bit `n` is zero.
