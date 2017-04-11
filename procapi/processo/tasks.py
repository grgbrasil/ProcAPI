from celery import Celery

app = Celery('procapi_task')

@app.task
def add(x, y):
    return x + y

# celery -A tasks worker --loglevel=info
