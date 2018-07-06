from celery import Celery
from time import sleep

celery_app = Celery('worker', broker='amqp://guest@queue//')

# celery_app.conf.task_routes = {
#     'app.worker.test_celery': 'main-queue',
# }

@celery_app.task()
def test_celery(word: str):
    sleep(5)
    print('test task')
    return 'test task return {word}'
