#!/usr/bin/env bash
set -u
if command -v analyzeHeadless >/dev/null 2>&1; then
    printf 'OK:analyzeHeadless:%s\n' "$(command -v analyzeHeadless)"
    exit 0
fi
printf 'INSTALL_OPTIONAL:ghidra_analyzeHeadless\n'
exit 0
