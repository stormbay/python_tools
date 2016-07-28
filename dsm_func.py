import sys, getopt
import subprocess

major, minor=sys.version_info[:2]
if (major != 3) or (minor < 4):
    print("This script requires python3.4 or newer to run!")
    print("You seem to be running: " + sys.version)
    sys.exit(1)


need_new_symbol_file=False

nm="aarch64-linux-gnu-nm"
objdump="aarch64-linux-gnu-objdump"

elffile="vmlinux"
symfile="System.map"


opts, args=getopt.getopt(sys.argv[1:], "f:", ["elf=", "symbol="])
for opt, value in opts:
    if opt=="--elf":
        elffile=value
    elif opt=="--symbol":
        symfile=value
        need_new_symbol_file=True
    elif opt=="-f":
        target_symbol=value
    else:
        sys.exit(1) 


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

