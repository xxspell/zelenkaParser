import json

import aiohttp
import asyncio
import time

import structlog


logger = structlog.get_logger(__name__)


class RateLimiter:
    def __init__(self, max_requests, interval):
        self.max_requests = max_requests
        self.interval = interval
        self.tokens = max_requests
        self.last_request_time = 0

    async def _wait(self):
        now = time.time()
        elapsed_time = now - self.last_request_time

        if elapsed_time < self.interval:
            remaining_time = self.interval - elapsed_time
            logger.info(f"Waiting for {remaining_time:.2f} seconds before making the next request...")
            await asyncio.sleep(self.interval - elapsed_time)

        self.tokens = self.max_requests
        self.last_request_time = time.time()

    async def acquire(self):
        if self.tokens <= 0:
            await self._wait()

        self.tokens -= 1


class AsyncLolzAPI:
    def __init__(self, base_url, access_token, max_requests=20, interval=60):
        self.base_url = base_url
        logger.debug(
            "Initializing LolzAPI", base_url=base_url, access_token=access_token
        )
        self.access_token = access_token
        self.headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}",
        }
        self.rate_limiter = RateLimiter(max_requests, interval)

    async def _request(self, method, url, payload=None, key=None, value=None):
        async with aiohttp.ClientSession() as session:
            if key and value is not None:
                self.headers[key] = value
            async with session.request(method, url, data=payload, headers=self.headers) as response:
                logger.debug('Request', method=method, url=url, payload=payload, headers=self.headers)
                return await response.json(), response.status

    async def get_thread(self, thread_id):
        await self.rate_limiter.acquire()
        url = f"{self.base_url}/threads/{thread_id}"
        return await self._request('GET', url)

    async def create_post(self, thread_id, post_body):
        await self.rate_limiter.acquire()
        url = f"{self.base_url}/posts?thread_id={thread_id}"
        payload = {"post_body": "+"}
        header_key = "content-type"
        header_value = "application/x-www-form-urlencoded"
        return await self._request("POST", url, payload, header_key, header_value)

    async def get_post_comments(self, post_id):
        await self.rate_limiter.acquire()
        url = f"{self.base_url}/posts/{post_id}/comments"
        return await self._request("GET", url)


class AsyncProxyManagerAPI:
    def __init__(self, base_url):
        self.base_url = base_url

    async def _request(self, method, url, payload=None, headers=None):
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, json=payload, headers=headers) as response:
                logger.debug(response.headers)
                logger.debug(response.status)

                return await response.text()

    async def add_proxy(self, login, password, ip, port, type_proxy="http"):
        url = f"{self.base_url}/proxymanager/api/proxies/add_proxy/"
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {"type": type_proxy, "login": login, "password": password, "ip": ip, "port": port}

        return await self._request("POST", url=url, payload=payload, headers=headers)

    async def check_proxy(self, proxy_id):
        url = f"{self.base_url}/proxymanager/api/proxies/{proxy_id}/check_proxy/"
        headers = {
            'Content-Type': 'application/json'
        }
        return await self._request("POST", url=url, headers=headers)
