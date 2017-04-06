
import sys, os.path
import math, struct, string
from collections import namedtuple

class HashLevel(object):
    def __init__(self, size):
        self.start = 0
        self.size = size


class VerityImage(object):

    def __init__(self, file):
        self.HASH_SIZE = 32
        self.BLOCK_SIZE = 4096
        self.FEC_BLOCK_SIZE = self.BLOCK_SIZE
        self.METADATA_SIZE = self.BLOCK_SIZE * 8

        self.file = file

        """
        Sync FEC header format with <system/extras/libfec/include/fec/io.h>

        /* disk format for the header */
        struct fec_header {
            uint32_t magic;
            uint32_t version;
            uint32_t size;
            uint32_t roots;
            uint32_t fec_size;
            uint64_t inp_size;
            uint8_t hash[SHA256_DIGEST_LENGTH];
        } __attribute__ ((packed));
        """
        self.FEC_HEADER_FORMAT = 'IIIIIII32s'
        self.FEC_HEADER_SIZE = struct.calcsize(self.FEC_HEADER_FORMAT)
        self.FEC_Header = namedtuple('FECHeader', 'magic version size roots fec_size inp_size inp_high hash')

        self.METADATA_HEADER_FORMAT = 'II256sI'
        self.METADATA_HEADER_SIZE = struct.calcsize(self.METADATA_HEADER_FORMAT)
        self.METADATA_Header = namedtuple('METAHeader', 'magic version signature length')

    def parse(self):
        self.fd = open(self.file, "rb")

        """
        Parse FEC Header
        """
        self.fd.seek(-self.FEC_BLOCK_SIZE, os.SEEK_END)
        fec_raw = self.fd.read(self.FEC_HEADER_SIZE)
        self.FecHdr1 = self.FEC_Header._make(struct.unpack(self.FEC_HEADER_FORMAT, fec_raw))
        self.FecHdr1_inp_size = (self.FecHdr1.inp_high << 32) + self.FecHdr1.inp_size

        self.fd.seek(-self.FEC_HEADER_SIZE, os.SEEK_END)
        fec_raw = self.fd.read(self.FEC_HEADER_SIZE)
        self.FecHdr2 = self.FEC_Header._make(struct.unpack(self.FEC_HEADER_FORMAT, fec_raw))
        self.FecHdr2_inp_size = (self.FecHdr2.inp_high << 32) + self.FecHdr2.inp_size

        """
        Parse METADATA
        """
        self.METADATA_OFFSET = self.FecHdr1_inp_size - self.METADATA_SIZE

        self.fd.seek(self.METADATA_OFFSET, os.SEEK_SET)
        metadata_raw = self.fd.read(self.METADATA_HEADER_SIZE)
        self.MetaHdr = self.METADATA_Header._make(struct.unpack(self.METADATA_HEADER_FORMAT, metadata_raw))

        """
        Parse Mapping Table
        """
        self.MAPPING_TABLE_OFFSET = self.METADATA_OFFSET + self.METADATA_HEADER_SIZE
        self.MAPPING_TABLE_SIZE = self.MetaHdr.length

        self.fd.seek(self.MAPPING_TABLE_OFFSET, os.SEEK_SET)
        mapping_table_raw = self.fd.read(self.MAPPING_TABLE_SIZE)
        self.MappingTable = mapping_table_raw.split()
        self.MappingTable_length = len(self.MappingTable)

        self.datablock_count = int(self.MappingTable[5])
        self.hashblock_offset = int(self.MappingTable[6])
        self.root_digest = self.MappingTable[8].decode().upper()

        self.fd.close()

        self.calc_hash_levels()

    def calc_hash_levels(self):
        self.hash_levels = []
        hashblks = self.datablock_count
        while True:
            hashblks = (hashblks + 127) // 128
            level = HashLevel(hashblks)
            self.hash_levels.append(level)
            if hashblks == 1:
                break
        levels = len(self.hash_levels)
        self.hash_levels[levels-1].start = self.hashblock_offset
        for i in range(levels-1, 0, -1):
            self.hash_levels[i-1].start = self.hash_levels[i].start + self.hash_levels[i].size

    def search_hash(self, blkid):
        print("")

        offset = 0
        levels = len(self.hash_levels)
        max_blockid = self.hash_levels[0].start + self.hash_levels[0].size - 1
        if blkid < 0 or blkid > max_blockid :
            print("Error: Incorrect block index \"%d\"" % blkid)
            return
        if blkid < self.datablock_count:
            offset = (self.hash_levels[0].start + blkid // 128) * self.BLOCK_SIZE + (blkid % 128) * self.HASH_SIZE
        elif blkid == self.hash_levels[levels-1].start:
            print("==== ROOT Digest ====")
            print("%s\n" % self.root_digest)
            return
        else:
            for i in range(levels-1):
                if blkid > self.hash_levels[i].start and blkid < (self.hash_levels[i].start + self.hash_levels[i].size):
                    blkid -= self.hash_levels[i].start
                    offset = (self.hash_levels[i+1].start + blkid // 128) * self.BLOCK_SIZE + (blkid % 128) * self.HASH_SIZE

        self.fd = open(self.file, "rb")
        self.fd.seek(offset, os.SEEK_SET)
        hash_raw = self.fd.read(self.HASH_SIZE)
        self.fd.close()

        print("==== Digest @0x%X ====" % offset)
        print("%02X " * 32 % struct.unpack("32B", hash_raw))
        print("")

    def show_fec(self):
        print("==== FEC Header 1 ====")
        print("[magic]:     %X" % self.FecHdr1.magic)
        print("[version]:   %d" % self.FecHdr1.version)
        print("[size]:      %d" % self.FecHdr1.size)
        print("[roots]:     %d" % self.FecHdr1.roots)
        print("[fec_size]:  %d" % self.FecHdr1.fec_size)
        print("[inp_size]:  %d" % self.FecHdr1_inp_size)
        print("[hash]:      " + "%02X "*32 % struct.unpack("32B", self.FecHdr1.hash))
        print("")

        print("==== FEC Header 2 ====")
        print("[magic]:     %X" % self.FecHdr2.magic)
        print("[version]:   %d" % self.FecHdr2.version)
        print("[size]:      %d" % self.FecHdr2.size)
        print("[roots]:     %d" % self.FecHdr2.roots)
        print("[fec_size]:  %d" % self.FecHdr2.fec_size)
        print("[inp_size]:  %d" % self.FecHdr2_inp_size)
        print("[hash]:      " + "%02X " * 32 % struct.unpack("32B", self.FecHdr2.hash))
        print("")

    def show_metadata(self):
        print("==== METADATA ====")
        print("[magic]:     %X" % self.MetaHdr.magic)
        print("[version]:   %d" % self.MetaHdr.version)
        print("[size]:      %d" % self.MetaHdr.length)
        print("[signature]: " + "%02X "*256 % struct.unpack("256B", self.MetaHdr.signature))
        print("")

    def show_mapping_table(self):
        print("==== Mapping Table ====")
        print("[version]:           %s" % int(self.MappingTable[0]))
        print("[data device]:       %s" % self.MappingTable[1].decode())
        print("[hash device]:       %s" % self.MappingTable[2].decode())
        print("[data block size]:   %s" % int(self.MappingTable[3]))
        print("[hash block size]:   %s" % int(self.MappingTable[4]))
        print("[data block number]: %s" % int(self.MappingTable[5]))
        print("[hash block offset]: %s" % int(self.MappingTable[6]))
        print("[hash algorithm]:    %s" % self.MappingTable[7].decode())
        print("[root digest]:       %s" % self.MappingTable[8].decode().upper())
        print("[salt]:              %s" % self.MappingTable[9].decode().upper())
        print("")

    def show_hashlevels(self):
        levels = len(self.hash_levels)
        print("==== %d Levels Hash Tree ====" % levels)
        for i in range(levels):
            print("Level[%d]: Start Block: %d, Size: %d blocks" % (i, self.hash_levels[i].start, self.hash_levels[i].size))
        print("")

    def show_all(self):
        print("")
        self.show_fec()
        self.show_metadata()
        self.show_mapping_table()
        self.show_hashlevels()


if __name__ == "__main__":

    import getopt

    def usage():
        genout="Usage: "+sys.argv[0]+" "
        genlen=len(genout)
        genoff=" "*genlen
        print(genout + "-d --img=<verity-image-file>" + "\t// show FEC & Verity Info")
        print(genout + "-s --img=<verity-image-file> --blk=<block index> " + "\t// Searh Hash in Metadata for <blk>")

    imgfile=""
    blkid=-1

    FLAG_SHOW_INFO = 1
    FLAG_SEARCH_HASH = 2
    ACTION_FLAGS = 0

    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    opts, args = getopt.getopt(sys.argv[1:], "dsh", ["img=","blk=",])
    for opt, value in opts:
        if opt == "-d":
            ACTION_FLAGS |= FLAG_SHOW_INFO
        elif opt == "-s":
            ACTION_FLAGS |= FLAG_SEARCH_HASH
        elif opt == "--img":
            imgfile = value
        elif opt == "--blk":
            blkid = int(value)
        else:
            usage()
            sys.exit(1)

    if imgfile == "":
        usage()
        sys.exit(1)
    if not os.path.exists(imgfile):
        print("Error: Image file \""+imgfile+"\" doesn't exist.")
        sys.exit(1)

    vimg = VerityImage(imgfile)
    vimg.parse()

    if (ACTION_FLAGS & FLAG_SHOW_INFO) != 0:
        vimg.show_all()

    if (ACTION_FLAGS & FLAG_SEARCH_HASH) != 0:
        vimg.search_hash(blkid)
