
import sys, os.path, getopt


print_prompt=sys.argv[0]+": "

def usage():
	genout="Usage: "+sys.argv[0]+" "
	genlen=len(genout)
	genoff=" "*genlen
	print(genout+"--if=<input-file> [--of=<output-file>] --start=<offset-in-file> --size=<size-in-byte>")
	print(genoff+"\b\b\b\bOR: -i <input-file> [-o <output-file>] -s <offset-in-file> -l <size-in-byte>")


infile=""
outfile=""
offset=0
total_size=0
actual_size=0

BLOCK_READ_SIZE=0x100000

if len(sys.argv)<2:
	usage()
	sys.exit(1)

opts, args=getopt.getopt(sys.argv[1:], "i:o:s:l:", ["if=", "of=", "start=", "size="])
for opt, value in opts:
	if (opt=="-i") or (opt=="--if"):
		infile=value
	elif (opt=="-o") or (opt=="--of"):
		outfile=value
	elif (opt=="-s") or (opt=="--start"):
		offset=int(value, base=16)
	elif (opt=="-l") or (opt=="--size"):
		total_size=int(value, base=16)
	else:
		usage()
		sys.exit(1)

if infile=="":
	usage()
	sys.exit(1)
if not os.path.exists(infile):
	print(print_prompt+"Error: Input file \""+infile+"\" doesn't exist.")
	sys.exit(1)

if outfile=="":
	outfile="t-"+infile+"-"+str(hex(offset))+"-"+str(hex(total_size))

if total_size==0:
	print(print_prompt+"\"size\" is 0, no data need truncated.")
	sys.exit(0)

ifp=open(infile, "rb")
ofp=open(outfile, "wb")

ifp.seek(offset)

while actual_size < total_size:
	size=total_size - actual_size
	if size > BLOCK_READ_SIZE:
		size=BLOCK_READ_SIZE

	rddata=ifp.read(size)
	rdsize=len(rddata)

	ofp.write(rddata)

	actual_size+=rdsize

	if rdsize < BLOCK_READ_SIZE:
		break

ifp.close()
ofp.close()

print(print_prompt+"DONE! - %d bytes data truncated into \"%s\"." % (actual_size, outfile))
