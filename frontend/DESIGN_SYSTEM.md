# 🎨 Единая дизайн-система CRM

## Обзор

Данная дизайн-система основана на Ant Design и обеспечивает единообразный внешний вид всех компонентов приложения.

## 🎯 Принципы

1. **Консистентность** - все компоненты следуют единым правилам дизайна
2. **Доступность** - поддержка WCAG 2.1 стандартов
3. **Адаптивность** - корректное отображение на всех устройствах
4. **Производительность** - оптимизированные компоненты и стили

## 🎨 Цветовая палитра

### Основные цвета
- **Primary**: `#1890ff` - основной цвет бренда
- **Success**: `#52c41a` - успешные действия
- **Warning**: `#faad14` - предупреждения
- **Error**: `#ff4d4f` - ошибки
- **Info**: `#1890ff` - информационные сообщения

### Нейтральные цвета
- **Text Primary**: `rgba(0, 0, 0, 0.88)` - основной текст
- **Text Secondary**: `rgba(0, 0, 0, 0.65)` - вторичный текст
- **Text Tertiary**: `rgba(0, 0, 0, 0.45)` - третичный текст
- **Text Disabled**: `rgba(0, 0, 0, 0.25)` - отключенный текст

### Фоны
- **Background Primary**: `#ffffff` - основной фон
- **Background Secondary**: `#fafafa` - вторичный фон
- **Background Tertiary**: `#f5f5f5` - третичный фон

### Границы
- **Border Primary**: `#d9d9d9` - основные границы
- **Border Secondary**: `#f0f0f0` - вторичные границы

## 📝 Типографика

### Шрифт
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
```

### Размеры шрифтов
- **xs**: `12px` - очень мелкий текст
- **sm**: `14px` - мелкий текст
- **base**: `16px` - основной текст
- **lg**: `18px` - крупный текст
- **xl**: `20px` - очень крупный текст
- **2xl**: `24px` - заголовки
- **3xl**: `30px` - крупные заголовки
- **4xl**: `36px` - очень крупные заголовки

### Начертания
- **normal**: `400` - обычное
- **medium**: `500` - среднее
- **semibold**: `600` - полужирное
- **bold**: `700` - жирное

## 📏 Отступы и размеры

### Базовые отступы
- **xs**: `4px`
- **sm**: `8px`
- **md**: `16px`
- **lg**: `24px`
- **xl**: `32px`
- **2xl**: `48px`
- **3xl**: `64px`

### Радиусы скругления
- **sm**: `2px` - мелкие элементы
- **base**: `6px` - стандартные элементы
- **lg**: `8px` - крупные элементы
- **xl**: `12px` - очень крупные элементы
- **full**: `9999px` - полностью круглые

## 🎭 Компоненты

### Общие компоненты

#### PageWithTable
Универсальный компонент для страниц с таблицами.

```jsx
import { PageWithTable } from '../components/CommonComponents';

<PageWithTable
  title="Заголовок страницы"
  data={data}
  columns={columns}
  loading={loading}
  onRefresh={handleRefresh}
  onAdd={handleAdd}
  showAddButton={true}
  showRefreshButton={true}
/>
```

#### FormModal
Модальное окно с формой.

```jsx
import { FormModal, FormField } from '../components/CommonComponents';

<FormModal
  title="Заголовок модального окна"
  visible={modalVisible}
  onOk={handleSubmit}
  onCancel={handleCancel}
  form={form}
>
  <FormField.Input
    name="fieldName"
    label="Название поля"
    placeholder="Плейсхолдер"
    rules={[formUtils.createRules.required()]}
  />
</FormModal>
```

#### FormField
Набор готовых полей формы.

```jsx
// Текстовое поле
<FormField.Input
  name="name"
  label="Имя"
  placeholder="Введите имя"
  rules={[formUtils.createRules.required()]}
/>

// Выпадающий список
<FormField.Select
  name="category"
  label="Категория"
  placeholder="Выберите категорию"
  options={[
    { value: '1', label: 'Категория 1' },
    { value: '2', label: 'Категория 2' }
  ]}
/>

// Текстовое поле
<FormField.TextArea
  name="description"
  label="Описание"
  placeholder="Введите описание"
  rows={4}
/>
```

### Специализированные компоненты

#### StatusTag
Отображение статусов с цветовой индикацией.

```jsx
import { StatusTag } from '../components/CommonComponents';

<StatusTag status="pending" />
<StatusTag status="active" />
<StatusTag status="completed" />
```

#### MoneyDisplay
Отображение денежных сумм с цветовой индикацией.

```jsx
import { MoneyDisplay } from '../components/CommonComponents';

<MoneyDisplay amount={1000} currency="₽" />
<MoneyDisplay amount={-500} currency="₽" />
<MoneyDisplay amount={0} currency="₽" colorize={false} />
```

#### DateDisplay
Отображение дат в едином формате.

```jsx
import { DateDisplay } from '../components/CommonComponents';

<DateDisplay date="2024-01-15" />
<DateDisplay date="2024-01-15" format="DD.MM.YYYY HH:mm" />
```

## 🛠️ Утилиты

### formUtils
Утилиты для работы с формами.

```jsx
import { formUtils } from '../components/CommonComponents';

// Создание правил валидации
const rules = [
  formUtils.createRules.required('Поле обязательно'),
  formUtils.createRules.min(2, 'Минимум 2 символа'),
  formUtils.createRules.max(100, 'Максимум 100 символов'),
  formUtils.createRules.email(),
  formUtils.createRules.phone(),
];

// Обработка ошибок API
formUtils.handleApiError(error, 'Сообщение по умолчанию');

// Показ успешного сообщения
formUtils.showSuccess('Операция выполнена успешно');
```

### useApi
Хук для работы с API.

```jsx
import { useApi } from '../components/CommonComponents';

const { loading, error, execute } = useApi();

const handleSubmit = async () => {
  await execute(async () => {
    const response = await api.post('/endpoint', data);
    return response.data;
  });
};
```

## 🎨 CSS классы

### Утилиты для отступов
```css
.p-0, .p-1, .p-2, .p-3, .p-4, .p-5  /* padding */
.m-0, .m-1, .m-2, .m-3, .m-4, .m-5  /* margin */
```

### Утилиты для flexbox
```css
.d-flex, .d-inline-flex
.flex-column, .flex-row
.justify-content-between, .justify-content-center
.align-items-center, .align-items-start, .align-items-end
```

### Утилиты для текста
```css
.text-center, .text-left, .text-right
.text-primary, .text-success, .text-warning, .text-error, .text-muted
```

### Утилиты для фона
```css
.bg-primary, .bg-success, .bg-warning, .bg-error, .bg-light, .bg-white
```

### Утилиты для границ
```css
.border, .border-top, .border-bottom, .border-left, .border-right
.border-radius, .border-radius-sm, .border-radius-lg
```

### Утилиты для размеров
```css
.w-100, .h-100, .w-auto, .h-auto
```

## 📱 Адаптивность

### Брейкпоинты
- **xs**: `480px` - мобильные устройства
- **sm**: `576px` - планшеты
- **md**: `768px` - малые экраны
- **lg**: `992px` - средние экраны
- **xl**: `1200px` - большие экраны
- **xxl**: `1600px` - очень большие экраны

### Адаптивные классы
```css
.d-none-mobile    /* Скрыть на мобильных */
.d-block-mobile   /* Показать на мобильных */
```

## 🎭 Анимации

### Fade In
```css
.fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
```

### Slide In
```css
.slide-in {
  animation: slideIn 0.3s ease-in-out;
}
```

## 📋 Рекомендации по использованию

### 1. Всегда используйте общие компоненты
Вместо создания собственных компонентов используйте готовые из `CommonComponents`.

### 2. Следуйте цветовой палитре
Не используйте произвольные цвета, всегда применяйте цвета из дизайн-системы.

### 3. Используйте правильные отступы
Применяйте стандартные отступы из дизайн-системы для консистентности.

### 4. Соблюдайте типографику
Используйте правильные размеры и начертания шрифтов.

### 5. Тестируйте на разных устройствах
Убедитесь, что интерфейс корректно отображается на всех размерах экранов.

## 🔧 Настройка темы

Тема настраивается в файле `src/utils/designSystem.js`:

```jsx
export const antdTheme = {
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
    // ... другие настройки
  },
  components: {
    // Настройки для конкретных компонентов
  },
};
```

## 📚 Дополнительные ресурсы

- [Ant Design Documentation](https://ant.design/docs/react/introduce)
- [Ant Design Icons](https://ant.design/components/icon)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) 