# Ghidra Jython script. Run with analyzeHeadless -postScript export_strings.py out.json
import json

from ghidra.program.model.data import StringDataInstance
from ghidra.program.util import DefinedDataIterator


def to_hex(addr):
    return "0x%x" % addr.getOffset()


args = getScriptArgs()
out_path = args[0] if len(args) >= 1 else "/tmp/ghidra-strings.json"

strings = []
for data in DefinedDataIterator.definedStrings(currentProgram):
    inst = StringDataInstance.getStringDataInstance(data)
    value = inst.getStringValue() if inst else None
    if value:
        strings.append({"address": to_hex(data.getAddress()), "value": value[:500]})

with open(out_path, "w") as f:
    json.dump({"program": currentProgram.getName(), "strings": strings}, f, indent=2, sort_keys=True)

print("WROTE:%s" % out_path)
