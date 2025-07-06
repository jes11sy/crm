from django.core.management.base import BaseCommand
from core.models import Roli, Polzovateli

class Command(BaseCommand):
    help = 'Проверка ролей и пользователей в базе данных'

    def handle(self, *args, **options):
        self.stdout.write("=== РОЛИ В БАЗЕ ДАННЫХ ===")
        for role in Roli.objects.all():
            self.stdout.write(f"ID: {role.id}, Название: '{role.name}'")

        self.stdout.write("\n=== ПОЛЬЗОВАТЕЛИ В БАЗЕ ДАННЫХ ===")
        for user in Polzovateli.objects.all():
            role_name = user.rol.name if user.rol else "Нет роли"
            self.stdout.write(f"ID: {user.id}, Имя: '{user.name}', Логин: '{user.login}', Роль: '{role_name}'")

        self.stdout.write("\n=== ПРОВЕРКА ПРАВ ДОСТУПА ===")
        admin_users = Polzovateli.objects.filter(rol__name='admin')
        director_users = Polzovateli.objects.filter(rol__name='director')
        master_users = Polzovateli.objects.filter(rol__name='master')
        kc_users = Polzovateli.objects.filter(rol__name='kc')

        self.stdout.write(f"Администраторов: {admin_users.count()}")
        self.stdout.write(f"Директоров: {director_users.count()}")
        self.stdout.write(f"Мастеров: {master_users.count()}")
        self.stdout.write(f"КЦ пользователей: {kc_users.count()}") 