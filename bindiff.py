import sys
import getopt, struct


def usage():
	print("Usage: "+sys.argv[0]+" -f1 <file1> -f2 <file2> -o <diff-output-file>")

"""
if len(sys.argv) < 2:
	usage()
	sys.exit(1)

opts,args=getopt.getopt(sys.argv[1], "o:", ["f1=", "f2="])

for opt,value in opts:
	if opt=="-o":
		pass
	elif opt=="--f1":
		pass
	elif opt=="--f2":
		pass
	else:
		usage()
		sys.exit(1)
"""

file1_name="vmlinux"
file2_name="vmlinux2"
outfile_name="bin.diff"

block_size=4096
section_size=128
line_size=32

block_num=0
diff_count=0

fn1=open(file1_name, 'rb')
fn2=open(file2_name, 'rb')
of=open(outfile_name, 'w')

def show_section_diff(sec1, sec2, secoft):
	len1=len(sec1)
	len2=len(sec2)
	minlen=min(len1, len2)

	global diff_count

	n=0
	out1=''
	out2=''
	while n < minlen:
		val1=struct.unpack_from('<I', sec1, n)[0]
		val2=struct.unpack_from('<I', sec2, n)[0]

		offset=secoft + n

		if (n % section_size)==0:
			of.write(out1)
			of.write(out2)
			out1="\n\n<<"+file1_name+">>"
			out2="\n<<"+file2_name+">>"

		if (n % line_size)==0:
			out1+="\n {0:>08X}:".format(offset)
			out2+="\n {0:>08X}:".format(offset)

		if not val1==val2:
			diff_count+=1
			out1+=" >{0:>08X}".format(val1)
			out2+=" >{0:>08X}".format(val2)
		else:
			out1+="  {0:>08X}".format(val1)
			out2+="  {0:>08X}".format(val2)

		n+=4

	of.write(out1)
	of.write(out2)

while True:
	data1=fn1.read(block_size)
	data2=fn2.read(block_size)

	if (min(len(data1), len(data2))<block_size):
		break;

	if data1==data2:
		block_num+=1
		continue

	secoff=0
	while secoff < block_size:
		sec1=data1[secoff:(secoff+section_size)]
		sec2=data2[secoff:(secoff+section_size)]

		if not sec1==sec2:
			show_section_diff(sec1, sec2, (block_num * block_size + secoff))

		secoff+=section_size

	block_num+=1


if diff_count==0:
	of.write("No difference.\n")


fn1.close()
fn2.close()
of.close()
