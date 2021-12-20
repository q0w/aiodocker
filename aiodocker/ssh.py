import functools
from typing import Dict, List, Optional, Union, cast

import asyncssh
from aiohttp.client import ClientTimeout
from aiohttp.client_exceptions import UnixClientConnectorError
from aiohttp.client_proto import ResponseHandler
from aiohttp.client_reqrep import ClientRequest
from aiohttp.connector import UnixConnector
from aiohttp.helpers import ceil_timeout, sentinel
from aiohttp.tracing import Trace


class SSHResponseHandler(ResponseHandler):
    def session_started(self):
        pass

    def data_received(self, data: bytes, datatype: Optional[int]) -> None:
        #        assert datatype is not None
        #  assert self.transport is not None
        super().data_received(data)


class SSHUnixConnector(UnixConnector):
    def __init__(
        self,
        path: str,
        host: str,
        ssh_options: Optional[Dict[str, str]],
        force_close: bool = False,
        keepalive_timeout: Union[object, float, None] = sentinel,
        limit: int = 100,
        limit_per_host: int = 0,
    ):
        super().__init__(
            path=path,
            force_close=force_close,
            keepalive_timeout=keepalive_timeout,
            limit=limit,
            limit_per_host=limit_per_host,
        )
        self._host = host
        self._ssh_options = ssh_options
        self._factory = functools.partial(SSHResponseHandler, loop=self._loop)

    @property
    def host(self):
        return self._host

    @property
    def ssh_options(self):
        return self._ssh_options

    async def _create_connection(
        self, req: "ClientRequest", traces: List["Trace"], timeout: "ClientTimeout"
    ) -> ResponseHandler:
        try:
            async with ceil_timeout(timeout.sock_connect):
                conn = await asyncssh.connect(
                    self.host, **self.ssh_options
                ).__aenter__()
                _, proto = await conn.create_unix_connection(self._factory, self.path)
        except OSError as exc:
            raise UnixClientConnectorError(self.path, req.connection_key, exc) from exc
        return cast(ResponseHandler, proto)


# class SSHTCPConnector(TCPConnector):
#     def __init__(
#         self,
#         host: str,
#         ssh_options: Dict[Optional[str, str]],
#         verify_ssl: bool = True,
#         fingerprint: Optional[bytes] = None,
#         use_dns_cache: bool = True,
#         ttl_dns_cache: Optional[int] = 10,
#         family: int = 0,
#         ssl_context: Optional[SSLContext] = None,
#         ssl: Union[None, bool, Fingerprint, SSLContext] = None,
#         local_addr: Optional[Tuple[str, int]] = None,
#         resolver: Optional[AbstractResolver] = None,
#         keepalive_timeout: Union[None, float, object] = sentinel,
#         force_close: bool = False,
#         limit: int = 100,
#         limit_per_host: int = 0,
#         enable_cleanup_closed: bool = False,
#         loop: Optional[asyncio.AbstractEventLoop] = None,
#     ):
#         super(SSHTCPConnector, self).__init__(
#             verify_ssl=verify_ssl,
#             fingerprint=fingerprint,
#             use_dns_cache=use_dns_cache,
#             ttl_dns_cache=ttl_dns_cache,
#             family=family,
#             ssl_context=ssl_context,
#             ssl=ssl,
#             local_addr=local_addr,
#             resolver=resolver,
#             keepalive_timeout=keepalive_timeout,
#             force_close=force_close,
#             limit=limit,
#             limit_per_host=limit_per_host,
#             enable_cleanup_closed=enable_cleanup_closed,
#             loop=loop,
#         )
#         self._host = host
#         self._ssh_options = ssh_options
#         self._factory = functools.partial(SSHResponseHandler, loop=self._loop)
#
#     @property
#     def host(self):
#         return self._host
#
#     @property
#     def ssh_options(self):
#         return self._ssh_options
#
#     async def _create_connection(
#         self, req: "ClientRequest", traces: List["Trace"], timeout: "ClientTimeout"
#     ) -> ResponseHandler:
#         try:
#             async with ceil_timeout(timeout.sock_connect):
#                 conn = await asyncssh.connect(
#                     self.host, **self.ssh_options
#                 ).__aenter__()
#                 _, proto = await conn.create_connection(self._factory, self.path)
#         except OSError as exc:
#             raise ClientConnectorError(self.path, req.connection_key, exc) from exc
#         return cast(ResponseHandler, proto)
