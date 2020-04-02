class dev:
    ver = '0.0.8'
    BROKER = '192.168.48.42'
    PORT = 8883
    KEEP_ALIVE = 10
    TLS = True

class test:
    ver = '0.0.8'
    BROKER = 'box.huihecloud.com'
    PORT = 8883
    KEEP_ALIVE = 10
    TLS = True

class pro:
    ver = '0.0.8'
    BROKER = 'api.huihecloud.com'
    PORT = 1883
    KEEP_ALIVE = 10
    TLS = False

config = test