from aiohttp import web, ClientSession
import asyncio
import random
import prometheus_client
import os
from prometheus_counters import PrometheusCounters

routes = web.RouteTableDef()
backend_pool = os.environ.get('BACKEND_POOL', 'localhost:8081').replace(" ", "").split(",")
metrics_port = int(os.environ.get('METRICS_PORT', "8000"))
MAX_DELAY_MS = 64000
MAX_RANDOM_DELAY_MS = 100
MIN_RANDOM_DELAY_MS = 0
p_counters = PrometheusCounters()


async def distribute_request_to_pool(request: web.Request) -> web.Response:
    tasks = [asyncio.create_task(forward_request(request, domain)) for domain in backend_pool]
    finished, unfinished = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for finish_task in finished:
        return web.Response(**finish_task.result())


async def forward_request(request: web.Request, dst_domain: str, delay_ms: int = 0, max_attempts: int = 100):
    async with ClientSession() as session:
        # Not opening new session on retries
        for i in range(max_attempts):
            await asyncio.sleep(delay_ms / 1000)
            try:
                async with session.post('http://' + dst_domain + str(request.rel_url),
                                        data=await request.read(),
                                        headers=request.headers) as resp:

                    if resp.status == 201:
                        p_counters.prometheus_inc_success_counter(dst_domain)
                        return await parse_response_to_dict(resp)

                    p_counters.prometheus_inc_failed_counter(dst_domain)
                    if delay_ms <= 0:
                        delay_ms = 1000
                    random_ms = random.randint(MIN_RANDOM_DELAY_MS, MAX_RANDOM_DELAY_MS)
                    delay_ms = min(delay_ms * 2, MAX_DELAY_MS) + random_ms
                    print(f'did not receive status code 201- request to {dst_domain} will retry in {delay_ms} ms')
            except Exception as e:
                p_counters.prometheus_inc_failed_counter(dst_domain)
                print(f'failed to send request with error: {e}')
                print(f'failed to send request to {dst_domain} will retry in {delay_ms} ms')


async def parse_response_to_dict(response):
    return {'status': response.status, 'headers': response.headers, 'body': await response.read()}


@routes.get('/')
async def home(request):
    return web.Response(text="You should try hitting /register or /changePassword using POST method")


@routes.post('/register')
async def register(request: web.Request):
    return await distribute_request_to_pool(request)


@routes.post('/changePassword')
async def change_password(request):
    return await distribute_request_to_pool(request)


def main():
    prometheus_client.start_http_server(metrics_port)
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)


if __name__ == '__main__':
    main()



