import sys
import getopt


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
block_num=0
diff_count=0

fn1=open(file1_name, 'rb')
fn2=open(file2_name, 'rb')
of=open(outfile_name, 'w')

def show_block_diff(dat1, dat2, blk):
	len1=len(dat1)
	len2=len(dat2)
	print("len1=%d, len2=%d" %(len1, len2))

	pass

while True:
	data1=fn1.read(block_size)
	data2=fn2.read(block_size)

	if not data1==data2:
		show_block_diff(data1, data2, block_num)
		diff_count+=1

	block_num+=1
	break

if diff_count==0:
	of.write("No difference.\n")


fn1.close()
fn2.close()
of.close()
