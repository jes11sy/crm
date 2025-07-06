#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 Анализ размера бандла...');

try {
  // Создаем production build
  console.log('📦 Создание production build...');
  execSync('npm run build', { stdio: 'inherit' });
  
  // Анализируем размер бандла
  console.log('📊 Анализ размера файлов...');
  const buildPath = path.join(__dirname, '..', 'build', 'static', 'js');
  
  if (fs.existsSync(buildPath)) {
    const files = fs.readdirSync(buildPath);
    
    console.log('\n📋 Размер файлов JavaScript:');
    files.forEach(file => {
      if (file.endsWith('.js')) {
        const filePath = path.join(buildPath, file);
        const stats = fs.statSync(filePath);
        const sizeKB = (stats.size / 1024).toFixed(2);
        console.log(`  ${file}: ${sizeKB} KB`);
      }
    });
  }
  
  // Проверяем CSS файлы
  const cssPath = path.join(__dirname, '..', 'build', 'static', 'css');
  if (fs.existsSync(cssPath)) {
    const cssFiles = fs.readdirSync(cssPath);
    
    console.log('\n📋 Размер файлов CSS:');
    cssFiles.forEach(file => {
      if (file.endsWith('.css')) {
        const filePath = path.join(cssPath, file);
        const stats = fs.statSync(filePath);
        const sizeKB = (stats.size / 1024).toFixed(2);
        console.log(`  ${file}: ${sizeKB} KB`);
      }
    });
  }
  
  console.log('\n✅ Анализ завершен!');
  console.log('💡 Рекомендации:');
  console.log('  - Файлы больше 500KB стоит разбить на чанки');
  console.log('  - Используйте React.lazy() для крупных компонентов');
  console.log('  - Оптимизируйте изображения и иконки');
  
} catch (error) {
  console.error('❌ Ошибка при анализе:', error.message);
  process.exit(1);
} 