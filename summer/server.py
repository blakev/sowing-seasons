from tornado.ioloop import IOLoop

from summer import make_app

if __name__ == '__main__':
    app, settings = make_app()
    app.listen(settings.port)
    IOLoop.current().start()