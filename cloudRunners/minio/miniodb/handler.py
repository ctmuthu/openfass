from minio import Minio
from minio.error import ResponseError


def handle(req):
    client = Minio('138.246.234.122:9000',
                   access_key='access',
                   secret_key='secretkey',
                   secure=False)
    # Get a full object
    try:
        data = client.get_object('test', 'IMG_0685.HEIC')
        return data
    except ResponseError as err:
        return err
