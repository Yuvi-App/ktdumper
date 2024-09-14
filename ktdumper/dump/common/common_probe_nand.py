class CommonProbeNand:

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.nand_cmd = opts["nand_cmd"]
        self.nand_addr = opts["nand_addr"]
        self.nand_data = opts["nand_data"]
        self.sweep = opts["sweep"]

    def read_id(self, base):
        self.writeb(0x90, base + self.nand_cmd)
        self.writeb(0x00, base + self.nand_addr)
        ret = b""
        for x in range(5):
            h = self.readh(base + self.nand_data)
            ret += bytes([h & 0xFF, (h >> 8) & 0xFF])
        return ret

    def execute(self, dev, output):
        super().execute(dev, output)

        for addr in range(self.sweep, 2**32, 0x1000000):
            print("0x{:08X} :: {}".format(addr, self.read_id(addr).hex()))
