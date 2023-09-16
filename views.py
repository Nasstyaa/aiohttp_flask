from aiohttp import web
from models import Session, AdModel

async def app_context(app: web.Application):
    print('START')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print('SHUTDOWN')


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request['session'] = session
        response = await handler(request)
        return response



class AdvView(web.View):

    @property
    def session(self) -> Session:
        return self.request['session']

    @property
    def advertisement_id(self) -> int:
        return int(self.request.match_info['adv_id'])

    async def get(self):
       adv = await self.session.get(AdModel, self.advertisement_id)
       if adv in not None:
           return web.json_response({
                'id': adv.id,
                'title': adv.title,
                'created_at': adv.created_at,
                'description': adv.description,
                'owner': adv.owner,
            })
       return web.json_response({'error': 'Advertisement not found'})


    async def post(self):
        data = await self.request.json()
        if bool("title" and "description" and "owner" not in data.keys()):
            raise web.HTTPBadRequest()
        create = await AdModel.create_model(**data)
        return web.json_response(create.to_dict())
            })

    async def patch(self):
        data = await self.request.json()
        adv = int(self.request.match_info["advertisements_id"])
        updated_data = await AdModel.update_model(adv, **data)
        return web.json_response(updated_data.to_dict())

    async def delete(self):
        adv = int(self.request.match_info["advertisements_id"])
        get_adv = await AdModel.by_id(adv)
        if not get_adv:
            return web.HTTPNotFound()
        await get_adv.delete()
        return web.HTTPNoContent()

async def create_app():
    app = web.Application()

    app.cleanup_ctx.append(app_context)
    app.middlewares.append(session_middleware)

    app.router.add_route('GET', '/advertisements/{advertisement_id}', AdvView)
    app.router.add_route('POST', '/advertisements', AdvView)
    app.router.add_route('PATCH', '/advertisements/{advertisement_id}', AdvView)
    app.router.add_route('DELETE', '/advertisements/{advertisement_id}', AdvView)

    return app


if __name__ == '__main__':
    web.run_app(create_app(), host='localhost', port=8080)