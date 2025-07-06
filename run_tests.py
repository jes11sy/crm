#!/usr/bin/env python
"""
Скрипт для запуска всех тестов CRM системы
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def setup_django():
    """Настройка Django для тестов"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'panel.settings')
    django.setup()

def run_tests():
    """Запуск всех тестов"""
    setup_django()
    
    # Получаем тестовый раннер
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Запускаем тесты
    failures = test_runner.run_tests([
        'core.tests.test_models',
        'core.tests.test_serializers', 
        'core.tests.test_views',
        'core.tests.test_permissions',
        'core.tests.test_utils'
    ])
    
    return failures

def run_specific_tests(test_pattern=None):
    """Запуск конкретных тестов"""
    setup_django()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    if test_pattern:
        failures = test_runner.run_tests([test_pattern])
    else:
        failures = test_runner.run_tests(['core.tests'])
    
    return failures

def run_tests_with_coverage():
    """Запуск тестов с покрытием кода"""
    try:
        import coverage
    except ImportError:
        print("coverage не установлен. Установите: pip install coverage")
        return 1
    
    # Начинаем измерение покрытия
    cov = coverage.Coverage()
    cov.start()
    
    # Запускаем тесты
    failures = run_tests()
    
    # Останавливаем измерение покрытия
    cov.stop()
    cov.save()
    
    # Выводим отчёт
    print("\n" + "="*50)
    print("ОТЧЁТ О ПОКРЫТИИ КОДА")
    print("="*50)
    cov.report()
    
    # Сохраняем HTML отчёт
    cov.html_report(directory='htmlcov')
    print(f"\nHTML отчёт сохранён в папке: htmlcov/")
    
    return failures

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Запуск тестов CRM системы')
    parser.add_argument('--coverage', action='store_true', 
                       help='Запустить тесты с измерением покрытия кода')
    parser.add_argument('--pattern', type=str,
                       help='Запустить конкретные тесты (например: core.tests.test_models)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Запуск тестов CRM системы...")
        print(f"Покрытие: {'Да' if args.coverage else 'Нет'}")
        if args.pattern:
            print(f"Паттерн: {args.pattern}")
    
    try:
        if args.coverage:
            failures = run_tests_with_coverage()
        elif args.pattern:
            failures = run_specific_tests(args.pattern)
        else:
            failures = run_tests()
        
        if failures:
            print(f"\n❌ Тесты завершились с {failures} ошибками")
            sys.exit(1)
        else:
            print("\n✅ Все тесты прошли успешно!")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Ошибка при запуске тестов: {e}")
        sys.exit(1) 