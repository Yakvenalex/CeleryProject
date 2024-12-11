import requests
from celery import Celery
from app.config import ssl_options, redis_url, settings

# Создаем экземпляр приложения Celery
celery_app = Celery("celery_worker", broker=redis_url, backend=redis_url)

# Настройки Celery
celery_app.conf.update(
    broker_use_ssl=ssl_options,
    redis_backend_use_ssl=ssl_options,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    enable_utc=True,  # Убедитесь, что UTC включен
    timezone='Europe/Moscow',  # Устанавливаем московское время
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)


@celery_app.task(
    name='delete_file_scheduled',
    bind=True,
    max_retries=3,
    default_retry_delay=5
)
def delete_file_scheduled(self, file_id, dell_id):
    """Задача для отложенного удаления файла"""
    try:
        response = requests.delete(f"{settings.BASE_URL}/delete/{file_id}/{dell_id}")
        response.raise_for_status()
        return response.status_code
    except requests.RequestException as exc:
        self.retry(exc=exc)
    except Exception as e:
        return None

