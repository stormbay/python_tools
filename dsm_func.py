import sys, os.path
import getopt
import subprocess

import gen_utils

"""
major, minor=sys.version_info[:2]
if (major != 3) or (minor < 4):
    print("This script requires python3.4 or newer to run!")
    print("You seem to be running: " + sys.version)
    sys.exit(1)
"""

def usage():
    print("Usage: "+sys.argv[0]+" [--32bit] --elf=<elf-file> -f <function> [--symbol=<symbol-file>]")


mode_32bit=False
need_new_symbol_file=True

elffile=""
symfile=""


if len(sys.argv)<2:
    usage()
    sys.exit(1)

opts, args=getopt.getopt(sys.argv[1:], "f:", ["32bit", "elf=", "symbol="])
for opt, value in opts:
    if opt=="--elf":
        elffile=value
    elif opt=="--symbol":
        symfile=value
    elif opt=="--32bit":
        mode_32bit=True
    elif opt=="-f":
        target_symbol=value
    else:
        usage()
        sys.exit(1)

plat = gen_utils.get_system_type()

if mode_32bit==True:
    if plat == 'Linux' :
        nm="arm-linux-gnueabi-nm"
        objdump="arm-linux-gnueabi-objdump"
    elif plat == 'Windows' :
        nm="arm-none-eabi-nm"
        objdump="arm-none-eabi-objdump"
else:
    nm="aarch64-linux-gnu-nm"
    objdump="aarch64-linux-gnu-objdump"

if elffile=="":
    usage()
    sys.exit(1)
if not os.path.exists(elffile):
    print("Error: ELF file \""+elffile+"\" doesn't exist.")
    sys.exit(1)

if symfile=="":
    symfile=elffile+".map"
else:
    if not os.path.exists(symfile):
        print("Error: Symbol file \""+symfile+"\" doesn't exist.")
        sys.exit(1)
    need_new_symbol_file=False


get_sym_cmd=nm+" -n "+elffile+" | grep -v '\( [aNUw] \)\|\(__crc_\)\|\( \$[adt]\)' > "+symfile
if need_new_symbol_file is True:
    print(get_sym_cmd)
    subprocess.call(get_sym_cmd, shell=True)

fn=open(symfile, 'r')
lines=[]
for count, line in enumerate(fn):
    lines.append((count, line.rstrip('\n')))
count+=1
fn.close()

for n in range(count):
    cell=lines[n][1].split(' ')
    if (cell[1].upper() == "T") and (cell[2] == target_symbol):
        break;
next=lines[n+1][1].split(' ')

saddr=cell[0]
eaddr=next[0]
asmfile=cell[2]+".S"

disassemble_cmd=objdump+" -d"+" --start-address=0x"+saddr+" --stop-address=0x"+eaddr+" "+elffile+" > "+asmfile

print(disassemble_cmd)
subprocess.call(disassemble_cmd, shell=True)

