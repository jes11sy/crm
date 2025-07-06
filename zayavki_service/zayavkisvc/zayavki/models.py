from django.db import models

# Create your models here.

class TipZayavki(models.Model):
    """Тип заявки"""
    name = models.CharField('Тип заявки', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Тип заявки'
        verbose_name_plural = 'Типы заявок'
        ordering = ['name']

    def __str__(self):
        return self.name

class Zayavka(models.Model):
    """Заявка"""
    tip = models.ForeignKey(TipZayavki, on_delete=models.PROTECT, verbose_name='Тип заявки')
    title = models.CharField('Заголовок', max_length=200)
    description = models.TextField('Описание')
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    status = models.CharField('Статус', max_length=50, default='new')
    # user_id, master_id — для интеграции с User Service (сохраняем id)
    user_id = models.IntegerField('ID пользователя')
    master_id = models.IntegerField('ID мастера', null=True, blank=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

class ZayavkaFile(models.Model):
    """Файл заявки"""
    zayavka = models.ForeignKey(Zayavka, on_delete=models.CASCADE, related_name='files', verbose_name='Заявка')
    file = models.FileField('Файл', upload_to='zayavka_files/')
    uploaded_at = models.DateTimeField('Загружен', auto_now_add=True)

    class Meta:
        verbose_name = 'Файл заявки'
        verbose_name_plural = 'Файлы заявок'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Файл для заявки {self.zayavka_id}"
