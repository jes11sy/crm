# 📁 Структура Frontend

## 🎯 Организация страниц

### Основные страницы
- `HomePage.js` - главная страница с дашбордом
- `LoginPage.js` - страница входа
- `LogoutPage.js` - страница выхода

### Страницы мастера (`pages/master/`)
- `MasterDashboard.js` - главный дашборд мастера
- `MasterFeedbackPage.js` - форма обратной связи
- `FinansiMasterPage.js` - финансы мастера
- `StatistikaMasterPage.js` - статистика работы
- `ZayvkiMasterPage.js` - заявки мастера
- `ZayavkaMasterDetailPage.js` - детали заявки
- `MasterPage.js` - профиль мастера

### Административные страницы (`pages/admin/`)
- `GorodPage.js` - управление городами
- `PolzovateliPage.js` - управление пользователями
- `RoliPage.js` - управление ролями
- `RKPage.js` - управление РК
- `PhoneGorodaPage.js` - телефоны городов
- `TipZayavkiPage.js` - типы заявок
- `TipTranzakciiPage.js` - типы транзакций

### Отчёты (`pages/reports/`)
- `AvitoReportPage.js` - отчёт по Avito
- `CityReportPage.js` - отчёт по городам
- `MasterReportPage.js` - отчёт по мастерам
- `KCStatsPage.js` - статистика КЦ

### Финансы
- `KassaPage.js` - касса
- `TranzakciiPage.js` - транзакции
- `DirectorPayoutsPage.js` - выплаты (для директора)

### Заявки
- `ZayavkiPage.js` - управление заявками
- `EditZayavkaPage.js` - редактирование заявки
- `VkhodyashchieZayavkiPage.js` - входящие заявки
- `EditVkhodyashchayaZayavkaPage.js` - редактирование входящей заявки

### Mango интеграция (`pages/mango/`)
- `MangoEmailPage.js` - управление email
- `MangoImportPage.js` - импорт данных

## 🧩 Компоненты (`components/`)
- `ErrorBoundary.js` - обработка ошибок

## 🎣 Hooks (`hooks/`)
- `useAuth.js` - аутентификация

## 🛠 Утилиты (`utils/`)
- `api.js` - API клиент

## 🎨 Стили
- `App.css` - основные стили приложения
- `index.css` - глобальные стили
- `MangoEmailPage.css` - стили для страницы Mango
- `MangoImportPage.css` - стили для импорта Mango

## 📱 Особенности
- Адаптивный дизайн
- Современный UI/UX
- Интеграция с Telegram
- Система уведомлений
- Кэширование данных 