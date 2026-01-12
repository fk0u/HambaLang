import sys
sys.path.insert(0, 'interpreter')
from hamba_v2 import HambaInterpreter

# Test extract function args
interp = HambaInterpreter()
line = 'tambahArray(arr, "C")'
start_pos = line.index('(') + 1

print(f"Line: {repr(line)}")
print(f"Start pos: {start_pos}")
print(f"Substring from start: {repr(line[start_pos:])}")

args_str = interp._extract_function_args(line, start_pos)
print(f"Extracted args: {repr(args_str)}")


