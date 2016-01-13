import os

from tornado.ioloop import IOLoop

from summer import make_app

if __name__ == '__main__':
    # fix the working directory
    # for non-IDE instances of the server process.
    path, file = os.path.split(__file__)
    os.chdir(path)

    app, settings = make_app()
    app.listen(settings.port, settings.host)

    print('Hosting on: http://%s:%s' % (settings.host, settings.port))

    IOLoop.current().start()