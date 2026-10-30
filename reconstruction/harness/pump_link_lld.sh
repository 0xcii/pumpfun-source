#!/bin/sh
# Rustc executes this hook directly; PATH may have an older Python or none.
exec "${PUMP_LINK_PYTHON:?link_order.configure must select Python}" "${0%/*}/pump_link_lld.py" "$@"
