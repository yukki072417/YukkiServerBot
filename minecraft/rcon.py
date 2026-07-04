"""
Minecraft RCON クライアント (非同期)
RCON プロトコル: https://wiki.vg/RCON
"""
import asyncio
import struct
from typing import Optional


class RconError(Exception):
    pass


class RconClient:
    _TYPE_AUTH = 3
    _TYPE_AUTH_RESP = 2
    _TYPE_COMMAND = 2
    _TYPE_RESPONSE = 0

    def __init__(self, host: str, port: int, password: str, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._next_id = 1

    async def connect(self):
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port),
            timeout=self.timeout,
        )
        await self._authenticate()

    async def _authenticate(self):
        req_id = self._next_id
        self._next_id += 1
        await self._write_packet(req_id, self._TYPE_AUTH, self.password)

        # Minecraft は認証成功時に type=2 / id=req_id、失敗時に id=-1 を返す
        # 一部のサーバーは先に空の type=0 パケットを送る
        while True:
            packet = await asyncio.wait_for(self._read_packet(), timeout=self.timeout)
            if packet['type'] == self._TYPE_AUTH_RESP:
                if packet['id'] == -1:
                    raise RconError('RCON 認証に失敗しました。パスワードを確認してください。')
                return
            # type=0 の空パケットはスキップ

    async def send_command(self, command: str) -> str:
        if self._writer is None:
            raise RconError('RCON に接続されていません。')
        req_id = self._next_id
        self._next_id += 1
        await self._write_packet(req_id, self._TYPE_COMMAND, command)
        packet = await asyncio.wait_for(self._read_packet(), timeout=self.timeout)
        return packet['payload']

    async def _write_packet(self, req_id: int, ptype: int, payload: str):
        encoded = payload.encode('utf-8')
        # length = id(4) + type(4) + payload + null(1) + padding(1)
        length = 10 + len(encoded)
        data = struct.pack('<iii', length, req_id, ptype) + encoded + b'\x00\x00'
        self._writer.write(data)
        await self._writer.drain()

    async def _read_packet(self) -> dict:
        size_data = await self._reader.readexactly(4)
        size = struct.unpack('<i', size_data)[0]
        data = await self._reader.readexactly(size)
        rid, rtype = struct.unpack('<ii', data[:8])
        payload = data[8:-2].decode('utf-8', errors='replace')
        return {'id': rid, 'type': rtype, 'payload': payload}

    async def close(self):
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass
            self._writer = None
            self._reader = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *_):
        await self.close()
