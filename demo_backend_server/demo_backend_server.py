from aiohttp import web
import random
import os

SKIP_SOME_REQUESTS = os.environ.get('SKIP_SOME_REQUESTS', 'true').lower()
SERVER_NAME = os.environ.get('SERVER_NAME', 'default_name')
SERVER_PORT = int(os.environ.get('SERVER_PORT', 8080))

routes = web.RouteTableDef()


async def log_and_prepare_response(request: web.Request, response_text: str):
    print('rel_url: ', request.rel_url)
    print('headers: ', request.headers)
    print('data: ', await request.read())
    if not random.randint(0, 4) and SKIP_SOME_REQUESTS == 'true':
        return web.Response(text='request dropped by server', status=500)
    return web.Response(text=response_text, status=201)


@routes.get('/')
async def home(request):
    return web.Response(text='You should try hitting /register or /changePassword using POST method')


@routes.get('/login')
async def home(request) -> web.Response:
    return web.Response(text=f'logged in on {SERVER_NAME}')


@routes.post('/register')
async def register(request: web.Request) -> web.Response:
    return await log_and_prepare_response(request, f'register on {SERVER_NAME}')


@routes.post('/changePassword')
async def change_password(request: web.Request) -> web.Response:
    return await log_and_prepare_response(request, f'password changed on {SERVER_NAME}')


def main():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, port=SERVER_PORT)


if __name__ == '__main__':
    main()
