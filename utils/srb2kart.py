from codecs import encode as cencode, decode as cdecode
from dataclasses import dataclass
from collections import namedtuple
from enum import Enum
import struct
import socket
import asyncio

############################################
# Helper functions and packet classes      #
# from https://github.com/JJK96/SRB2-Query #
############################################
def get_map_title(title, iszone, actnum):
    mapname = title
    if iszone:
        mapname += " zone"
    if actnum:
        mapname += f" {actnum}"
    return mapname

def char_to_num(char):
    return ord(char) - ord("A")

def mapname_to_num(mapname):
    if not mapname:
        return 0
    name = mapname[3:] # remove "MAP"
    try:
        num = int(name)
        return num
    except ValueError:
        p = char_to_num(name[0])
        try:
            q = int(name[1])
        except ValueError:
            q = 10 + char_to_num(name[1])
        return ((36*p + q) + 100)

num_to_skin = {
    0: "sonic",
    1: "tails",
    2: "knuckles",
    3: "amy",
    4: "fang",
    5: "metalsonic",
}

class PacketType(Enum):
    PT_ASKINFO         = 12
    PT_SERVERINFO      = 13
    PT_PLAYERINFO      = 14
    PT_TELLFILESNEEDED = 34
    PT_MOREFILESNEEDED = 35

def checksum(buf):
    """
    @param buf: buffer without the checksum part
    """
    c = 0x1234567
    for i, b in enumerate(buf):
        c += b * (i+1)
    return c

def checksum_match(buf, checksum):
    """
    Returns the index at which the checksum matches
    Or False if the checksum matches never
    @param buf: buffer including the checksum part
    """
    c = 0x1234567
    for i, b in enumerate(buf[4:]):
        c += b * (i+1)
        if (c == checksum):
            return i+4
    return False

def decode_string(byte_list):
    string = ""
    for b in byte_list:
        if b == 0:
            break
        if b <= 128:
            string += chr(b)
    return string

@dataclass
class Packet:
    type: PacketType

    def pack(self):
        if (self.type == PacketType.PT_ASKINFO):
            u = struct.pack("x"*5)
        else:
            raise Exception("Unknown type")
        pkt = struct.pack("xxBx", self.type.value) + u
        return struct.pack('<L', checksum(pkt)) + pkt

    def _add_to_dict(self, d):
        for k,v in d.items():
            self.__dict__[k] = v

    def unpack_common(self, pkt):
        """
        Unpack the first part of the packet, which is the same for every packet type.
        """
        header_length = 8
        format = "IBBBB"
        fields = "checksum ack ackreturn packettype reserved"
        t = namedtuple('Packet', fields)
        unpacked = t._asdict(t._make(struct.unpack(format, pkt[:header_length])))
        self._add_to_dict(unpacked)
        return pkt[header_length:]



class PlayerInfoPacket(Packet):

    def __init__(self, pkt):
        self.type = PacketType.PT_PLAYERINFO
        self.players = []
        self.unpack(pkt)

    def unpack(self, pkt):
        pkt = self.unpack_common(pkt)
        format_length = 36
        format = "<B22s4sBBBIH"
        fields = "num name address team skin data score timeinserver"
        for _ in range(32):
            t = namedtuple('Packet', fields)
            unpacked = t._asdict(t._make(struct.unpack(format, pkt[:format_length])))
            if (unpacked['num'] < 255):
                unpacked['name'] = decode_string(unpacked['name'])
                unpacked['skin'] = num_to_skin.get(unpacked['skin'], "unknown")
                self.players.append(unpacked)
            pkt = pkt[format_length:]

##############################
# Above sourced linked above #
##############################

#this is modified significantly from the original code above, to account for srb2kart's changes
class ServerInfoPacket(Packet): 
    def __init__(self, pkt):
        self.type = PacketType.PT_SERVERINFO
        self.unpack(pkt)

    def unpack(self, pkt):
        pkt = self.unpack_common(pkt)
        format_length = 382
        pformat = "<xB16sBBBBBBBBBII32s8s33s16sBB256s"
        pfields = "packetversion application version subversion numberofplayer maxplayer gametype modifiedgame cheatsenabled kartvarsmaybe fileneedednum leveltime time servername mapname maptitle mapmd5 actnum iszone httpserver"
        t = namedtuple('Packet', pfields)
        unpacked = t._asdict(t._make(struct.unpack(pformat, pkt[:format_length])))
        # mapformat8s33s16sBB:mapname maptitle mapmd5 actnum iszone
        string_fields = ["application","servername","httpserver","mapname","maptitle"]

        for s in string_fields:
            unpacked[s] = decode_string(unpacked[s])
        unpacked['mapmd5'] = cencode(unpacked['mapmd5'], 'base64').decode()
        unpacked['map'] =  {
            'num': mapname_to_num(unpacked['mapname']),
            'name': unpacked['mapname'],
            'title': get_map_title(unpacked['maptitle'], unpacked['iszone'], unpacked['actnum'])
        }
        self._add_to_dict(unpacked)

        
        flag_need = 0x01
        flag_dl = 0x10

        fileneeded = pkt[format_length:]
        self.fileneeded = []
        while len(fileneeded) > 20:
            filestatus, filesize = struct.unpack("<BI", fileneeded[:5])
            filestatus = {
                'neccessary' : bool(filestatus & flag_need),
                'downloadable' : bool(filestatus & flag_dl)
            }

            i = fileneeded.find(b'\x00', 5)+1
            filename = fileneeded[5:i-1].decode()
            fileneeded = fileneeded[i:]
            filemd5 = cencode(fileneeded[:16], 'base64').decode()
            fileneeded = fileneeded[16:]
            self.fileneeded.append({'name':filename, 'status':filestatus, 'size':filesize, 'md5':filemd5})


class SRB2QueryAsync:
    def __init__(self, url="localhost", port=5029):
        # self.on_con_lost = on_con_lost
        # self.transport = None

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect((url, port))
        
        pkt = Packet(PacketType.PT_ASKINFO)
        self.socket.sendall(pkt.pack())
    
    async def recv(self, loop):
        BUF_SIZE = 1450
        packet = await loop.sock_recv(self.socket, BUF_SIZE)
        cs = struct.unpack("I", packet[:4])[0]
        if cs == checksum(packet[4:]):
            return packet
        else:
            raise Exception("Incorrect checksum")

    # def connection_made(self, transport):
    #     self.transport = transport
    #     pkt = Packet(PacketType.PT_ASKINFO)
    #     self.transport.sendto(pkt.pack())

    # def datagram_received(self, data, addr):
    #     data
    #     self.transport.close()

    # def error_received(self, exc):
    #     pass

    # def connection_lost(self, exc):
    #     self.on_con_lost.set_result(True)


async def SRB2ping(url="localhost", port=5029):
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()


    # on_con_lost = loop.create_future()
    # transport, protocol = await loop.create_datagram_endpoint(
    #     lambda: Q3StatusClientProtocol(on_con_lost),
    #     remote_addr=('74.91.114.165', 5029))
    

    # Wait until the protocol signals that the connection
    # is lost and close the transport.
    # try:
    #     await on_con_lost
    # finally:
    #     transport.close()

    q = SRB2QueryAsync(url, port)

    a = loop.create_task(q.recv(loop))
    b = loop.create_task(q.recv(loop))

    await asyncio.wait([a,b])
    packets = [a.result(), b.result()]
    serverinfo = ServerInfoPacket(packets[0])
    playerinfo = PlayerInfoPacket(packets[1])
    print(serverinfo.__dict__)
    print()
    print(playerinfo.__dict__)
    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(SRB2ping('99.176.52.96', 5029))



#74.91.114.165
