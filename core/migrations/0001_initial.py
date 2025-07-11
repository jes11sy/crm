# Generated by Django 5.2.4 on 2025-07-05 10:08

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gorod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Город')),
            ],
            options={
                'verbose_name': 'Город',
                'verbose_name_plural': 'Города',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Roli',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название роли')),
            ],
            options={
                'verbose_name': 'Роль',
                'verbose_name_plural': 'Роли',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TipTranzakcii',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название транзакции')),
            ],
            options={
                'verbose_name': 'Тип транзакции',
                'verbose_name_plural': 'Типы транзакций',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TipZayavki',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Тип заявки')),
            ],
            options={
                'verbose_name': 'Тип заявки',
                'verbose_name_plural': 'Типы заявок',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Master',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Имя')),
                ('birth_date', models.DateField(verbose_name='Дата рождения')),
                ('passport', models.CharField(max_length=50, verbose_name='Паспорт')),
                ('phone', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='Номер телефона должен быть в формате: +999999999', regex='^\\+?1?\\d{9,15}$')], verbose_name='Номер телефона')),
                ('is_active', models.BooleanField(default=True, verbose_name='Работает')),
                ('chat_id', models.CharField(blank=True, max_length=50, null=True, verbose_name='ChatID')),
                ('note', models.TextField(blank=True, null=True, verbose_name='Примечание')),
                ('login', models.CharField(max_length=50, unique=True, verbose_name='Логин')),
                ('password', models.CharField(max_length=100, verbose_name='Пароль')),
                ('gorod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.gorod', verbose_name='Город')),
            ],
            options={
                'verbose_name': 'Мастер',
                'verbose_name_plural': 'Мастера',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PhoneGoroda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='Номер телефона должен быть в формате: +999999999', regex='^\\+?1?\\d{9,15}$')], verbose_name='Номер телефона')),
                ('gorod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.gorod', verbose_name='Город')),
            ],
            options={
                'verbose_name': 'Телефон города',
                'verbose_name_plural': 'Телефоны городов',
                'ordering': ['gorod', 'phone'],
            },
        ),
        migrations.CreateModel(
            name='RK',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rk_name', models.CharField(max_length=100, verbose_name='РК')),
                ('phone', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='Номер телефона должен быть в формате: +999999999', regex='^\\+?1?\\d{9,15}$')], verbose_name='Номер телефона')),
                ('gorod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.gorod', verbose_name='Город')),
            ],
            options={
                'verbose_name': 'РК',
                'verbose_name_plural': 'РК',
                'ordering': ['rk_name'],
            },
        ),
        migrations.CreateModel(
            name='Polzovateli',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Имя')),
                ('is_active', models.BooleanField(default=True, verbose_name='Статус')),
                ('login', models.CharField(max_length=50, unique=True, verbose_name='Логин')),
                ('password', models.CharField(max_length=100, verbose_name='Пароль')),
                ('note', models.TextField(blank=True, null=True, verbose_name='Примечание')),
                ('gorod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.gorod', verbose_name='Город')),
                ('rol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.roli', verbose_name='Роль')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tranzakcii',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summa', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Сумма')),
                ('note', models.TextField(blank=True, null=True, verbose_name='Примечание')),
                ('date', models.DateField(auto_now_add=True, verbose_name='Дата')),
                ('gorod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.gorod', verbose_name='Город')),
                ('tip_tranzakcii', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.tiptranzakcii', verbose_name='Тип транзакции')),
            ],
            options={
                'verbose_name': 'Транзакция',
                'verbose_name_plural': 'Транзакции',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Zayavki',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_client', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='Номер телефона должен быть в формате: +999999999', regex='^\\+?1?\\d{9,15}$')], verbose_name='Номер телефона клиента')),
                ('phone_atc', models.CharField(blank=True, max_length=20, null=True, validators=[django.core.validators.RegexValidator(message='Номер телефона должен быть в формате: +999999999', regex='^\\+?1?\\d{9,15}$')], verbose_name='Номер телефона ATC')),
                ('client_name', models.CharField(max_length=100, verbose_name='Имя клиента')),
                ('address', models.CharField(max_length=255, verbose_name='Адрес')),
                ('meeting_date', models.DateTimeField(verbose_name='Дата встречи')),
                ('tip_techniki', models.CharField(max_length=100, verbose_name='Тип техники')),
                ('problema', models.TextField(verbose_name='Проблема')),
                ('status', models.CharField(choices=[('Звонит', 'Звонит'), ('Ожидает', 'Ожидает'), ('В работе', 'В работе'), ('Готово', 'Готово'), ('Отказ', 'Отказ')], default='Ожидает', max_length=50, verbose_name='Статус')),
                ('itog', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Итог')),
                ('rashod', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Расход')),
                ('chistymi', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Чистыми')),
                ('sdacha_mastera', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Сдача мастера')),
                ('comment_master', models.TextField(blank=True, null=True, verbose_name='Комментарий мастера')),
                ('kc_name', models.CharField(max_length=100, verbose_name='Имя КЦ')),
                ('comment_kc', models.TextField(blank=True, null=True, verbose_name='Комментарий КЦ')),
                ('gorod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.gorod', verbose_name='Город')),
                ('master', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.master', verbose_name='Мастер')),
                ('rk', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.rk', verbose_name='РК')),
                ('tip_zayavki', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.tipzayavki', verbose_name='Тип заявки')),
            ],
            options={
                'verbose_name': 'Заявка',
                'verbose_name_plural': 'Заявки',
                'ordering': ['-meeting_date'],
            },
        ),
        migrations.CreateModel(
            name='ZayavkaFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='zayavka_files/')),
                ('type', models.CharField(choices=[('bso', 'БСО'), ('chek', 'Чек расхода'), ('audio', 'Аудиозапись')], max_length=10)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.polzovateli')),
                ('zayavka', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='core.zayavki')),
            ],
        ),
        migrations.AddIndex(
            model_name='master',
            index=models.Index(fields=['gorod', 'is_active'], name='core_master_gorod_i_d91c3c_idx'),
        ),
        migrations.AddIndex(
            model_name='master',
            index=models.Index(fields=['login'], name='core_master_login_e6c63e_idx'),
        ),
        migrations.AddIndex(
            model_name='phonegoroda',
            index=models.Index(fields=['phone'], name='core_phoneg_phone_949404_idx'),
        ),
        migrations.AddIndex(
            model_name='phonegoroda',
            index=models.Index(fields=['gorod', 'phone'], name='core_phoneg_gorod_i_da766d_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='phonegoroda',
            unique_together={('gorod', 'phone')},
        ),
        migrations.AlterUniqueTogether(
            name='rk',
            unique_together={('rk_name', 'gorod')},
        ),
        migrations.AddIndex(
            model_name='polzovateli',
            index=models.Index(fields=['gorod', 'is_active'], name='core_polzov_gorod_i_4a07ba_idx'),
        ),
        migrations.AddIndex(
            model_name='polzovateli',
            index=models.Index(fields=['login'], name='core_polzov_login_80dc70_idx'),
        ),
        migrations.AddIndex(
            model_name='polzovateli',
            index=models.Index(fields=['rol'], name='core_polzov_rol_id_8ad339_idx'),
        ),
        migrations.AddIndex(
            model_name='tranzakcii',
            index=models.Index(fields=['gorod', 'date'], name='core_tranza_gorod_i_40e615_idx'),
        ),
        migrations.AddIndex(
            model_name='tranzakcii',
            index=models.Index(fields=['tip_tranzakcii'], name='core_tranza_tip_tra_b49915_idx'),
        ),
        migrations.AddIndex(
            model_name='zayavki',
            index=models.Index(fields=['gorod', 'status'], name='core_zayavk_gorod_i_166cad_idx'),
        ),
        migrations.AddIndex(
            model_name='zayavki',
            index=models.Index(fields=['master'], name='core_zayavk_master__def4eb_idx'),
        ),
        migrations.AddIndex(
            model_name='zayavki',
            index=models.Index(fields=['rk'], name='core_zayavk_rk_id_fc6a5a_idx'),
        ),
        migrations.AddIndex(
            model_name='zayavki',
            index=models.Index(fields=['tip_zayavki'], name='core_zayavk_tip_zay_522047_idx'),
        ),
        migrations.AddIndex(
            model_name='zayavki',
            index=models.Index(fields=['phone_client'], name='core_zayavk_phone_c_b1c2e9_idx'),
        ),
        migrations.AddIndex(
            model_name='zayavki',
            index=models.Index(fields=['meeting_date'], name='core_zayavk_meeting_a2c292_idx'),
        ),
        migrations.AddIndex(
            model_name='zayavki',
            index=models.Index(fields=['phone_client', 'phone_atc', 'status'], name='core_zayavk_phone_c_afa1b6_idx'),
        ),
        migrations.AddIndex(
            model_name='zayavki',
            index=models.Index(fields=['status', 'gorod'], name='core_zayavk_status_158b0f_idx'),
        ),
        migrations.AddIndex(
            model_name='zayavki',
            index=models.Index(fields=['master', 'gorod'], name='core_zayavk_master__1b8dea_idx'),
        ),
        migrations.AddIndex(
            model_name='zayavki',
            index=models.Index(fields=['rk', 'gorod'], name='core_zayavk_rk_id_70a4eb_idx'),
        ),
    ]
