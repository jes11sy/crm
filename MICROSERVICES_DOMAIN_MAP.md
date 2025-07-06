# 🗺️ Карта доменов и зависимостей для микросервисов

| Сервис                | Модели/Модули                        | Основные зависимости           |
|-----------------------|--------------------------------------|-------------------------------|
| User Service          | core/models/users.py                  | Auth, Roles, JWT, Permissions |
| Zayavki Service       | core/models/requests.py, zayavka_files/ | User Service, Files           |
| Finance Service       | core/models/finance.py                | User Service, Zayavki Service |
| Report Service        | core/models/business.py, отчёты       | Все сервисы (чтение)          |
| Integration Service   | core/telegram_handler.py, mango, email| Все сервисы (уведомления)     |

## Связи между сервисами
- User Service ←→ Zayavki Service (мастер, клиент)
- User Service ←→ Finance Service (мастер, выплаты)
- Zayavki Service ←→ Finance Service (оплаты по заявкам)
- Report Service ←→ Все сервисы (чтение данных)
- Integration Service ←→ Все сервисы (уведомления, интеграции)

## Пример архитектуры
```
[User Service] <----> [Zayavki Service] <----> [Finance Service]
      |                      |                        |
      +----------------------+------------------------+
                             |
                    [Report Service]
                             |
                    [Integration Service]
```

---

_Документ обновляется по мере детализации миграции._ 