import sys, os.path
import re


class DumpData(object):

    def __init__(self):
        self.pc_start = 0
        self.pc_data_list = []
        self.lr_start = 0
        self.lr_data_list = []
        self.sp_start = 0
        self.sp_data_list = []

    def get_pc_data(self):
        return self.pc_start, self.pc_data_list

    def get_lr_data(self):
        return self.lr_start, self.lr_data_list

    def get_sp_data(self):
        return self.sp_start, self.sp_data_list

    def dump(self):
        start = self.pc_start
        total = len(self.pc_data_list)
        for n in range(total):
            print("0x{:08X}: 0x{:08X}".format(start, self.pc_data_list[n]))
            start += 4
        print()

        start = self.lr_start
        total = len(self.lr_data_list)
        for n in range(total):
            print("0x{:08X}: 0x{:08X}".format(start, self.lr_data_list[n]))
            start += 4
        print()

        start = self.sp_start
        total = len(self.sp_data_list)
        for n in range(total):
            print("0x{:08X}: 0x{:08X}".format(start, self.sp_data_list[n]))
            start += 4


class CacheData(DumpData):

    def __init__(self):
        super(CacheData, self).__init__()

    def extract(self, file):

        statinfo = os.stat(file)

        search_string = ["PC: 0x", "LR: 0x", "SP: 0x"]
        start_address = [self.pc_start, self.lr_start, self.sp_start]
        datadump_list = [self.pc_data_list, self.lr_data_list, self.sp_data_list]

        dmsgfd = open(file, 'r')

        idx = 0
        for lbuf in dmsgfd:
            result = re.search(search_string[idx], lbuf)
            if result != None:
                if idx == 0:
                    self.pc_start = int((lbuf[result.span()[1]:result.span()[1]+16]), 16)
                elif idx == 1:
                    self.lr_start = int((lbuf[result.span()[1]:result.span()[1] + 16]), 16)
                elif idx == 2:
                    self.sp_start = int((lbuf[result.span()[1]:result.span()[1] + 16]), 16)

                for i in range(16):
                    lbuf = dmsgfd.readline()
                    linelist = lbuf.split(' ')
                    num = len(linelist) - 4
                    for j in range(num):
                        datadump_list[idx].insert((i*num+j), int(linelist[j+4], 16))

                idx += 1
                if idx == 3:
                    break

        dmsgfd.close()


class MemData(DumpData):

    def __init__(self):
        super(MemData, self).__init__()

    def extract(self, file):

        statinfo = os.stat(file)

        start_address = [self.pc_start, self.lr_start, self.sp_start]
        datadump_list = [self.pc_data_list, self.lr_data_list, self.sp_data_list]

        mdfd = open(file, 'r')

        for lbuf in mdfd:
            result = re.search("address\|", lbuf)
            if result is not None:
                break

        for i in range(3):
            start = start_address[i]
            dlist = datadump_list[i]
            for lbuf in mdfd:

                result = re.search("address\|", lbuf)
                if result is not None:
                    break

                result = re.search("NSD:", lbuf)
                if result is None:
                    continue

                if i == 0 and self.pc_start == 0:
                    self.pc_start = int((lbuf[result.span()[1]:result.span()[1]+16]), 16)
                elif i == 1 and self.lr_start == 0:
                    self.lr_start = int((lbuf[result.span()[1]:result.span()[1] + 16]), 16)
                elif i == 2 and self.sp_start == 0:
                    self.sp_start = int((lbuf[result.span()[1]:result.span()[1] + 16]), 16)

                linelist = lbuf.replace("\n", "").replace(">", " ").split(' ')
                num = len(linelist) - 4
                offset = len(dlist)
                for j in range(num):
                    dlist.insert((offset + j), int(linelist[j + 4], 16))

        mdfd.close()


def verify_section(cache_start, cache_list, dump_start, dump_list):
    delta = 0
    delta_string = ""

    pop_num = (cache_start - dump_start) // 4
    for i in range(pop_num):
        dump_list.pop(0)

    count = min(len(cache_list), len(dump_list))
    for i in range(count):
        if cache_list[i] != dump_list[i]:
            delta += 1
            delta_string += "0x{:08X} |  0x{:08X}  0x{:08X}\n".format((cache_start+i*4), cache_list[i], dump_list[i])

    return delta, delta_string


def verify_data(dmesg_file, dump_file):

    cache_data = CacheData()
    cache_data.extract(dmesg_file)

    dump_data = MemData()
    dump_data.extract(dump_file)

    cache_start, cache_list = cache_data.get_pc_data()
    dump_start, dump_list = dump_data.get_pc_data()
    delta_pc, delta_pc_str = verify_section(cache_start, cache_list, dump_start, dump_list)

    cache_start, cache_list = cache_data.get_lr_data()
    dump_start, dump_list = dump_data.get_lr_data()
    delta_lr, delta_lr_str = verify_section(cache_start, cache_list, dump_start, dump_list)

    cache_start, cache_list = cache_data.get_sp_data()
    dump_start, dump_list = dump_data.get_sp_data()
    delta_sp, delta_sp_str = verify_section(cache_start, cache_list, dump_start, dump_list)

    result_str = "\n<------ PC ------>    Total: {:d}\n".format(delta_pc)
    result_str += delta_pc_str

    result_str += "\n<------ LR ------>    Total: {:d}\n".format(delta_lr)
    result_str += delta_lr_str

    result_str += "\n<------ SP ------>    Total: {:d}\n".format(delta_sp)
    result_str += delta_sp_str

    return result_str


if __name__ == "__main__":

    import getopt

    mode_32bit=False

    dmesg_file = ""
    dump_file = ""
    outfile = ""

    def usage():
        genout = "Usage: "+"\tcompare cache to memory data around PC/LR/SP"
        genout += "\n\t$ " + sys.argv[0] + " [--32bit] -d <dmesg-file> -m <memdump-file> [-o <output-file>]"
        print(genout)

    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    opts, args=getopt.getopt(sys.argv[1:], "d:m:o:", ["32bit"])
    for opt, value in opts:
        if opt=="-d":
            dmesg_file = value
        elif opt=="-m":
            dump_file = value
        elif opt=="-o":
            outfile = value
        elif opt=="--32bit":
            mode_32bit=True
        else:
            usage()
            sys.exit(1)

    if not os.path.exists(dmesg_file):
        print("Error: dmesg file \""+dmesg_file+"\" doesn't exist.")
        sys.exit(1)

    if not os.path.exists(dump_file):
        print("Error: dump file \""+dump_file+"\" doesn't exist.")
        sys.exit(1)

    result = verify_data(dmesg_file, dump_file)

    print(result)
    if outfile != "":
        out_fd = open(outfile, 'w')
        out_fd.write(result)
        out_fd.close()

