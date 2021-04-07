import asyncio

class tf2StatusClientProtocol:
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost
        self.transport = None
        self.result = None
    def connection_made(self, transport):
        prefix = bytes([255,255,255,255, 84])
        self.transport = transport
        self.transport.sendto(prefix+self.message.encode('utf-8')+bytes([0]))
    def datagram_received(self, data, addr):
        self.result=data

        self.transport.close()
    def error_received(self, exc):
        pass
    def connection_lost(self, exc):
        self.on_con_lost.set_result(True)

async def get_str(data):
    """return: (str, data)"""
    a = data.find(b'\x00')
    return data[:a].decode(), data[a+1:]
async def get_short(data):
    """return: (int, data)"""
    return int.from_bytes(data[:2], 'big'), data[2:]
async def get_long(data):
    """return: (int, data)"""
    return int.from_bytes(data[:4], 'big'), data[4:]
async def get_longlong(data):
    """return: (int, data)"""
    return int.from_bytes(data[:8], 'big'), data[8:]
async def get_float(data):
    """return: (float, data)"""
    return float.fromhex(data[:4], 'big'), data[4:]
async def get_byte(data):
    """return: (byte, data)"""
    return int.from_bytes([data[0],], 'big'), data[1:]

async def A2S_INFO_decode(data):
    data = data[5:]
    protocol, data = await get_byte(data)
    name, data = await get_str(data)
    smap, data = await get_str(data)
    folder, data = await get_str(data)
    game, data = await get_str(data)
    sid, data = await get_short(data)
    pl, data = await get_byte(data)
    maxpl, data = await get_byte(data)
    bots, data = await get_byte(data)
    stype, data = await get_byte(data)
    env, data = await get_byte(data)
    priv, data = await get_byte(data)
    vac, data = await get_byte(data)
    vers, data = await get_str(data)
    edv, data = await get_byte(data)
    if edv & 128:
        port, data = await get_short(data)
    else:
        port = None
    if edv & 16:
        steamid, data = await get_longlong(data)
    else:
        steamid = None
    if edv & 64:
        stvport, data = await get_short(data)
        stvname, data = await get_str(data)
    else:
       stvport, stvname = None, None
    if edv & 32:
        keywords, data = await get_str(data)
    else:
        keywords = None
    if edv & 1:
        gameid, data = await get_longlong(data)
    else:
        gameid = None
    stype = [x for x in ['Dedicated','Live','Proxy'] if x.startswith(chr(stype).upper())][0]
    env = [x for x in ['Linux','Windows','Mac'] if x.startswith(chr(env).upper())][0]
    return dict(name=name, map=smap, mod=folder, game=game, 
            steamappid=sid, players=pl, maxplayers=maxpl,
            bots=bots, servertype=stype, env=env,
            private=priv, secured=vac, version=vers, port=port, steamid=steamid, 
            stvport=stvport, stvname=stvname, keywords=keywords,
            gameid=gameid, sproto=protocol)


async def tf2ping():
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()
    message = 'Source Engine Query'

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: tf2StatusClientProtocol(message, on_con_lost),
        remote_addr=('74.91.114.165', 27015))
    try:
        await on_con_lost
    finally:
        transport.close()
    # It's very likely this isn't how I'm supposed to pass information out of this, but.... I don't care. - protocol.result 
    return await A2S_INFO_decode(protocol.result)