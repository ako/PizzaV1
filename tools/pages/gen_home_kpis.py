#!/usr/bin/env python3
"""Emit the repetitive KPI widgets of SCR-01 (40-cell pixel board, oven-slot and
courier unit icons) as MDL fragments; included into mdlsource/32-home.mdl."""
cells = '\n'.join(
    f"            container px{i} (Class: 'px-cell', DynamicClasses: if $currentObject/PxLit - 1 > {i} then 'on' else if $currentObject/PxLit - 1 = {i} then 'new' else '') {{ }}"
    for i in range(40))
ovens = '\n'.join(
    f"            container oven{i} (Class: 'unit', DynamicClasses: if $currentObject/Busy > {i} then 'on' else '', Visible: $currentObject/Slots > {i}) {{ dynamictext ovenIcon{i} (Content: 'local_fire_department', Class: 'ms') }}"
    for i in range(6))
cours = '\n'.join(
    f"            container cour{i} (Class: 'unit', DynamicClasses: if $currentObject/CouriersOn > {i} then 'on' else '', Visible: $currentObject/CouriersTotal > {i}) {{ dynamictext courIcon{i} (Content: 'electric_moped', Class: 'ms') }}"
    for i in range(5))
import sys
tpl = open(sys.argv[1]).read()
open(sys.argv[2], 'w').write(tpl.replace('%%PIXELS%%', cells).replace('%%OVENS%%', ovens).replace('%%COURIERS%%', cours))
