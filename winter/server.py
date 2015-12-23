from tornado.ioloop import IOLoop

from winter.settings import default as config
from winter import make_app

if __name__ == '__main__':
    app = make_app()

    app.listen(8888)
    IOLoop.current().start()