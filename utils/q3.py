import asyncio

class Q3StatusClientProtocol:
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost
        self.transport = None

    def connection_made(self, transport):
        prefix = bytes([255,255,255,255])
        self.transport = transport
        self.transport.sendto(prefix+self.message.encode())

    def datagram_received(self, data, addr):
        self.result=b'\n'.join(data.split(b'\n')[1:]).decode()
        self.transport.close()

    def error_received(self, exc):
        pass

    def connection_lost(self, exc):
        self.on_con_lost.set_result(True)


async def q3ping():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()
    message = 'getstatus\n'

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: Q3StatusClientProtocol(message, on_con_lost),
        remote_addr=('74.91.114.165', 27960))
    

    # Wait until the protocol signals that the connection
    # is lost and close the transport.
    try:
        await on_con_lost
    finally:
        transport.close()
    # It's very likely this isn't how I'm supposed to pass information out of this, but.... I don't care. 
    data = protocol.result.split('\n')
    split, pl = data[0].split('\\')[1:], data[1:-1]
    values = dict(zip(split[::2], split[1::2]))
    players = []
    for i in pl:
        players.append(dict(zip(['frags', 'ping', 'name'], i.split())))
    return (values, players)