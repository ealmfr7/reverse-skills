# Ghidra Jython script. Run with analyzeHeadless -postScript export_functions.py out.json module_name
import json
import sys

from ghidra.program.model.symbol import SourceType


def to_hex(addr):
    return "0x%x" % addr.getOffset()


args = getScriptArgs()
out_path = args[0] if len(args) >= 1 else "/tmp/ghidra-functions.json"
module_name = args[1] if len(args) >= 2 else currentProgram.getName()
image_base = currentProgram.getImageBase()

functions = []
fm = currentProgram.getFunctionManager()
for fn in fm.getFunctions(True):
    entry = fn.getEntryPoint()
    functions.append(
        {
            "name": fn.getName(),
            "entry": to_hex(entry),
            "offset": "0x%x" % (entry.getOffset() - image_base.getOffset()),
            "body_size": fn.getBody().getNumAddresses(),
            "is_thunk": fn.isThunk(),
            "source": str(fn.getSymbol().getSource()),
        }
    )

result = {
    "module": module_name,
    "program": currentProgram.getName(),
    "image_base": to_hex(image_base),
    "functions": functions,
}

with open(out_path, "w") as f:
    json.dump(result, f, indent=2, sort_keys=True)

print("WROTE:%s" % out_path)
