import struct
import tqdm

from dump.v2.rw_access_v2 import RwAccess_v2


class MlbaDumper_v2(RwAccess_v2):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.NAND_CMD = opts["nand_cmd"]
        self.NAND_ADDR = opts["nand_addr"]
        self.NAND_DATA = opts["nand_data"]

    def read_id(self):
        self.writeb(0x90, self.NAND_CMD)
        self.writeb(0x00, self.NAND_ADDR)
        ret = b""
        for x in range(5):
            ret += bytes([self.readh(self.NAND_DATA) & 0xFF])
        return ret

    def nand_wait(self):
        while True:
            self.writeb(0x70, self.NAND_CMD)
            data = self.readh(self.NAND_DATA)
            if data & 0x40:
                return data

    def nand_protocol_read4b(self, arg):
        self.writeb(0x00, self.NAND_CMD)
        self.writeb(arg, self.NAND_ADDR)
        self.writeb(0x00, self.NAND_ADDR)
        self.writeb(0x00, self.NAND_ADDR)
        self.writeb(0x00, self.NAND_ADDR)
        self.writeb(0x00, self.NAND_ADDR)
        self.writeb(0x57, self.NAND_CMD)

        self.nand_wait()
        self.writeb(0x00, self.NAND_CMD)

        return self.readh(self.NAND_DATA) | (self.readh(self.NAND_DATA) << 8) | (self.readh(self.NAND_DATA) << 16) | (self.readh(self.NAND_DATA) << 24)

    def _dump_with_cmd(self, dumpcmd, numpages, offset, outf_nand, outf_oob):
        with tqdm.tqdm(total=528*numpages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
            for x in range(numpages):
                self.usb_send(struct.pack("<BI", dumpcmd, offset + x))

                page = self.usb_receive()
                if page[0] == 0xE0:
                    page = page[1:]
                else:
                    print("read page 0x{:X} returned error 0x{:X}".format(x, page[0]))
                    page = b"\xFF" * 528

                assert len(page) == 528

                outf_nand.write(page[0:512])
                outf_oob.write(page[512:])

                bar.update(len(page))

    def execute(self, dev, output):
        super().execute(dev, output)

        print("=" * 80)

        print("NAND ID: {}".format(self.read_id().hex()))
        num_sda = self.nand_protocol_read4b(0xB5)
        num_mda = self.nand_protocol_read4b(0xB0)

        print("Num SDA: 0x{:X}".format(num_sda))
        print("Num MDA: 0x{:X}".format(num_mda))

        print("=" * 80)

        if num_sda:
            print("Dumping SDA")
            with output.mkfile("nand_sda.bin") as nand_sda_bin:
                with output.mkfile("nand_sda.oob") as nand_sda_oob:
                    self._dump_with_cmd(0x51, num_sda, 0x1000, nand_sda_bin, nand_sda_oob)

        if num_mda:
            print("Dumping MDA")
            with output.mkfile("nand_mda.bin") as nand_mda_bin:
                with output.mkfile("nand_mda.oob") as nand_mda_oob:
                    self._dump_with_cmd(0x50, num_mda, 0x200000, nand_mda_bin, nand_mda_oob)
