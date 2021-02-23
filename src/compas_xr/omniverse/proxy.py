from compas.rpc.services.default import start_service

def start(port, autoreload, **kwargs):
    start_service(port, autoreload)

if __name__ == '__main__':
    start(port=1753, autoreload=True)
