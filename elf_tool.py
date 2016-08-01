
import sys, os.path, getopt
import math, struct
from collections import namedtuple


# FIXME: TO Support 32-bit ELF


class Elf(object):

	def __init__(self, file):
		self.file = file

		self.ElfPHdrList = []
		self.ElfSHdrList = []

	def parse(self):
		self.fd = open( self.file, "rb")

		self.ELF64_HEADER_FORMAT   = '<16sHHIQQQIHHHHHH'
		self.ELF64_HEADER_SIZE     = struct.calcsize(self.ELF64_HEADER_FORMAT)
		self.ELF64_PGHEADER_FORMAT = '<IIQQQQQQ'
		self.ELF64_PGHEADER_SIZE   = struct.calcsize(self.ELF64_PGHEADER_FORMAT)
		self.ELF64_SHEADER_FORMAT  = '<IIQQQQIIQQ'
		self.ELF64_SHEADER_SIZE    = struct.calcsize(self.ELF64_SHEADER_FORMAT)

		self.Elf64Header   = namedtuple('ElfHeader',    'ident type machine version entry phoff shoff flags ehsize phentsize phnum shentsize shnum shstrndx')
		self.Elf64PgHeader = namedtuple('Elf64PHeader', 'type flags offset vaddr paddr filesz memsz align')
		self.Elf64SHeader  = namedtuple('Elf64SHeader', 'name type flags addr offset size link info align entsize')

		"""
		Parse ELF File Header
		"""
		header_raw  = self.fd.read(self.ELF64_HEADER_SIZE)
		self.ElfHdr = self.Elf64Header._make(struct.unpack(self.ELF64_HEADER_FORMAT, header_raw))

		"""
		Parse ELF Program Header
		"""
		for n in range(self.ElfHdr.phnum):
			self.fd.seek((self.ElfHdr.phoff + n * self.ELF64_PGHEADER_SIZE))
			pghdr_raw = self.fd.read(self.ELF64_PGHEADER_SIZE)
			elfphdr = self.Elf64PgHeader._make(struct.unpack(self.ELF64_PGHEADER_FORMAT, pghdr_raw))
			self.ElfPHdrList.append(elfphdr)

		"""
		Parse ELF Section Header
		"""
		SHT_STRTAB=3
		for n in range(self.ElfHdr.shnum):
			self.fd.seek((self.ElfHdr.shoff + n * self.ELF64_SHEADER_SIZE))
			shdr_raw = self.fd.read(self.ELF64_SHEADER_SIZE)
			elfshdr = self.Elf64SHeader._make(struct.unpack(self.ELF64_SHEADER_FORMAT, shdr_raw))
			self.ElfSHdrList.append(elfshdr)

		"""
		Read Section String Table
		"""
		self.str_table_list=[]
		str_table_idx=self.ElfHdr.shstrndx
		str_table_size=self.ElfSHdrList[str_table_idx].size
		self.fd.seek(self.ElfSHdrList[str_table_idx].offset)
		str_table_raw=self.fd.read(str_table_size)
		str_talbe = str_table_raw.decode(encoding='ascii')
		self.str_table_list.extend(str_talbe.split('\0'))
#		self.str_table_list.sort()

		self.fd.close()

	def show_hdr(self):
		print("[Ident]     %s" % self.ElfHdr.ident)
		print("[Type]      0x%x" % self.ElfHdr.type)
		print("[Machine]   %d" % self.ElfHdr.machine)
		print("[Version]   %d" % self.ElfHdr.version)
		print("[Entry]     0x%x" % self.ElfHdr.entry)
		print("[PhOff]     %d" % self.ElfHdr.phoff)
		print("[ShOff]     %d" % self.ElfHdr.shoff)
		print("[Flags]     0x%x" % self.ElfHdr.flags)
		print("[EhSize]    %d" % self.ElfHdr.ehsize)
		print("[PhEntSize] %d" % self.ElfHdr.phentsize)
		print("[Phnum]     %d" % self.ElfHdr.phnum)
		print("[ShEntSize] %d" % self.ElfHdr.shentsize)
		print("[ShNum]     %d" % self.ElfHdr.shnum)
		print("[ShStrndx]  %d" % self.ElfHdr.shstrndx)
		print("")

	def show_phdr(self):
		PF_R=4
		PF_W=2
		PF_X=1
		PT_LIST={		   0 : "NULL",
						   1 : "LOAD",
						   2 : "DYNAMIC",
						   3 : "INTERP",
						   4 : "NOTE",
						   5 : "SHLIB",
				  		   6 : "PHDR",
				  		   7 : "TLS",
				  0x60000000 : "LOOS",
				  0x6fffffff : "HIOS",
				  0x70000000 : "LOPROC",
				  0x7fffffff : "HIPROC",
				  0x6474e550 : "FRAME",
				  0x6474e551 : "STACK",}
		print("<< Program Header >>")
		for n in range(self.ElfHdr.phnum):
#			print("")
			ptype=PT_LIST[self.ElfPHdrList[n].type]
			print("[%8s]    off: 0x%016x vaddr: 0x%016x paddr: 0x%016x align: 2**%-2d" %
				  (ptype, self.ElfPHdrList[n].offset, self.ElfPHdrList[n].vaddr, self.ElfPHdrList[n].paddr, math.log2(self.ElfPHdrList[n].align)))
			pflag = ['-', '-', '-']
			if (self.ElfPHdrList[n].flags & PF_R):
				pflag[0]='R'
			if (self.ElfPHdrList[n].flags & PF_W):
				pflag[1]='W'
			if (self.ElfPHdrList[n].flags & PF_X):
				pflag[2]='X'
			print("           filesz: 0x%016x memsz: 0x%016x flags: %1s%1s%1s" %
				  (self.ElfPHdrList[n].filesz, self.ElfPHdrList[n].memsz, pflag[0], pflag[1], pflag[2]))
		print("")

	def shwo_string_table(self):
		list_len = len(self.str_table_list)
		print("<< String Table >>")
		print("")
		for n in range(list_len):
			name_str = self.str_table_list[n]
			print("%3d. [%s]" % (n, name_str))

	def show_shdr(self):
		ST_LIST = {			 0 : "NULL",
							 1 : "PROGBITS",
							 2 : "SYMTAB",
							 3 : "STRTAB",
							 4 : "RELA",
							 5 : "HASH",
							 6 : "DYNAMIC",
							 7 : "NOTE",
							 8 : "NOBITS",
							 9 : "REL",
							10 : "SHLIB",
							11 : "DYNSYM",
							12 : "NUM",
					0x70000000 : "LOPROC",
					0x7fffffff : "HIPROC",
					0x80000000 : "LOUSER",
					0x8fffffff : "HIUSER",}

		SF_WRITE=1
		SF_ALLOC=2
		SF_EXECINSTR=4
		SF_MASKPROC=0xf0000000

		print("<< Sections >>")
		list_len=len(self.str_table_list)
		for n in range(self.ElfHdr.shnum):
#			print("")
#			if self.ElfSHdrList[n].name < list_len:
#				name_str=self.str_table_list[self.ElfSHdrList[n].name]
#				print("%3d. [%s]" % (n, name_str))
#			else:
#				print("%3d. [%3d]" % (n, self.ElfSHdrList[n].name))

			type=ST_LIST[self.ElfSHdrList[n].type]
			flag=[]
			if (self.ElfSHdrList[n].flags & SF_WRITE):
				flag.append("WRITE")
			if (self.ElfSHdrList[n].flags & SF_ALLOC):
				flag.append("ALLOC")
			if (self.ElfSHdrList[n].flags & SF_EXECINSTR):
				flag.append("EXECINSTR")
			if (self.ElfSHdrList[n].flags & SF_MASKPROC):
				flag.append("MASKPROC")
			print("%3d. [%3d]  [Type]: %-8s  [Flags]: " % (n, self.ElfSHdrList[n].name, type), flag)

			if self.ElfSHdrList[n].align is 0:
				align=0
			else:
				align=math.log2(self.ElfSHdrList[n].align)
			print("     " "addr: 0x%016x" "  " "align: 2**%-2d" "  " "offset: 0x%08x" "  " "size: 0x%08x" %
				  (self.ElfSHdrList[n].addr, align, self.ElfSHdrList[n].offset, self.ElfSHdrList[n].size))

#			print("0x%x" % self.ElfSHdrList[n].link)
#			print("0x%x" % self.ElfSHdrList[n].info)
#			print("0x%x" % self.ElfSHdrList[n].entsize)
		print("")

		self.shwo_string_table()

	def show_all(self):
		self.show_hdr()
		self.show_phdr()
		self.show_shdr()

	def compare_section(self, dumpfile, secid, outputfile):
		if secid >= self.ElfHdr.shnum:
			return

		block_size=4096
		block_num=0
		diff_count=0

		sec_offset=self.ElfSHdrList[secid].offset
		sec_size=self.ElfSHdrList[secid].size
		sec_address=self.ElfSHdrList[secid].addr

		if self.ElfSHdrList[secid].align is 0:
			align=0
		else:
			align=math.log2(self.ElfSHdrList[secid].align)
		outstring="\"{:s}\"  Program Section ID: <{:d}>\n\n".format(self.file, secid)
		outstring+="Addr: 0x{:016X}  Align: 2**{:d}  Offset: 0x{:08X}  Size: 0x{:08X}\n".format(sec_address, int(align), sec_offset, sec_size)

		ef=open(self.file, 'rb')
		df=open(dumpfile, 'rb')
		of=open(outputfile, 'w')

		of.write(outstring)

		ef.seek(sec_offset)
		bin_offset=sec_address & ~0xFFFFFFC000000000
		df.seek(bin_offset)

		size_left=sec_size

		while True:

			if size_left==0:
				break;

			rdsize=block_size
			if size_left < block_size:
				rdsize=size_left

			data1=ef.read(rdsize)
			data2=df.read(rdsize)

			if (min(len(data1), len(data2)) < rdsize):
				break;

			size_left -= rdsize

			if data1==data2:
				block_num+=1
				continue

			secoff=0
			while secoff < rdsize:
				line_size=32
				slice_size=128
				if (rdsize - secoff) < 128:
					slice_size=rdsize - secoff

				sec1=data1[secoff:(secoff+slice_size)]
				sec2=data2[secoff:(secoff+slice_size)]

				if not sec1==sec2:
					len1=len(sec1)
					len2=len(sec2)
					minlen=min(len1, len2)

					n=0
					out1=''
					out2=''
					while n < minlen:
						val1=struct.unpack_from('<I', sec1, n)[0]
						val2=struct.unpack_from('<I', sec2, n)[0]

						offset=sec_size - size_left - rdsize + secoff + n

						if (n % slice_size)==0:
							of.write(out1)
							of.write(out2)
							out1="\n\n<<"+self.file+">>"
							out2="\n<<"+dumpfile+">>"

						if (n % line_size)==0:
							out1+="\n {0:>016X}:".format((sec_address + offset))
							out2+="\n {0:>016X}:".format((sec_address + offset))

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

				secoff+=slice_size

			block_num+=1

		if diff_count==0:
			of.write("No difference.\n")

		ef.close()
		df.close()
		of.close()

def usage():
	genout="Usage: "+sys.argv[0]+" "
	genlen=len(genout)
	genoff=" "*genlen
	print(genout+"-f --elf=<elf-file>"+"\t// show ELF file header")
	print(genoff+"-p --elf=<elf-file>"+"\t// show ELF program header")
	print(genoff+"-h --elf=<elf-file>"+"\t// show ELF section header")
	print(genoff+"-x --elf=<elf-file>"+"\t// show all ELF headers")
	print(genoff+"--elf=<elf-file> --bin=<dump-bin-file> --sid=<section-index> [--of=<output-file>]"+"\t// compare a section with memory dump")


elffile=""
binfile=""
outfile=""

FLAG_SHOW_FH=1
FLAG_SHOW_PH=2
FLAG_SHOW_SH=4
FLAG_SHOW_ALL=(FLAG_SHOW_FH | FLAG_SHOW_PH | FLAG_SHOW_SH)
FLAG_COMPARE_FLAG=8

ACTION_FLAGS=0

compare_section_id=0


if len(sys.argv)<2:
	usage()
	sys.exit(1)

opts, args=getopt.getopt(sys.argv[1:], "fphx", ["elf=", "bin=", "sid=", "of="])
for opt, value in opts:
	if opt=="-f":
		ACTION_FLAGS |= FLAG_SHOW_FH
	elif opt=="-p":
		ACTION_FLAGS |= FLAG_SHOW_PH
	elif opt=="-h":
		ACTION_FLAGS |= FLAG_SHOW_SH
	elif opt=="-x":
		ACTION_FLAGS |= FLAG_SHOW_ALL
	elif opt=="--elf":
		elffile=value
	elif opt=="--bin":
		binfile=value
		ACTION_FLAGS |= FLAG_COMPARE_FLAG
	elif opt=="--sid":
		compare_section_id=int(value)
	elif opt=="--of":
		outfile=value
	else:
		usage()
		sys.exit(1)

if elffile=="":
	usage()
	sys.exit(1)
if not os.path.exists(elffile):
	print("Error: ELF file \""+elffile+"\" doesn't exist.")
	sys.exit(1)


elf = Elf(elffile)
elf.parse()

if (ACTION_FLAGS & FLAG_SHOW_ALL) != 0:
	elf.show_all()
else:
	if (ACTION_FLAGS & FLAG_SHOW_FH) != 0:
		elf.show_hdr()
	if (ACTION_FLAGS & FLAG_SHOW_PH) != 0:
		elf.show_phdr()
	if (ACTION_FLAGS & FLAG_SHOW_SH) != 0:
		elf.show_shdr()

if (ACTION_FLAGS & FLAG_COMPARE_FLAG) != 0:
	if not os.path.exists(binfile):
		print("Error: Memory dump file \""+binfile+"\" doesn't exist.")
		sys.exit(1)
	if outfile=="":
		outfile="diff-"+binfile+"-section-"+str(compare_section_id)

	elf.compare_section(binfile, compare_section_id, outfile)
