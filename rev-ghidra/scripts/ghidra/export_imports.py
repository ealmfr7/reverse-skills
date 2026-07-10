# Ghidra Jython script. Run with analyzeHeadless -postScript export_imports.py out.json
import json


def to_hex(addr):
    return "0x%x" % addr.getOffset()


args = getScriptArgs()
out_path = args[0] if len(args) >= 1 else "/tmp/ghidra-imports.json"

imports = []
symbol_table = currentProgram.getSymbolTable()
for sym in symbol_table.getExternalSymbols():
    refs = []
    for ref in getReferencesTo(sym.getAddress()):
        refs.append(to_hex(ref.getFromAddress()))
    imports.append({"name": sym.getName(True), "references": refs[:200]})

with open(out_path, "w") as f:
    json.dump({"program": currentProgram.getName(), "imports": imports}, f, indent=2, sort_keys=True)

print("WROTE:%s" % out_path)
