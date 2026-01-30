#!/usr/bin/env python
"""
Исправление JavaScript для загрузки позывных из базы
"""
import os
import sys
import json

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.append('.')

import django
django.setup()

from django.contrib.auth.models import User
from tlog.models import RadioProfile

def fix_javascript():
    """Создаем исправленный JavaScript файл"""
    
    js_content = '''// Profile Edit JavaScript - ИСПРАВЛЕННАЯ ВЕРСИЯ
// ================================================

(function($) {
    'use strict';
    
    console.log('=== Profile Edit JS Loaded ===');
    
    // ========== Инициализация при загрузке страницы ==========
    
    function initProfileEdit() {
        console.log('Initializing profile edit...');
        
        // Загружаем данные из базы в форму
        loadProfileData();
        
        // Инициализируем обработчики событий
        initEventHandlers();
        
        // Инициализируем поля ввода позывных
        initCallsignInputs();
    }
    
    // Загрузка данных профиля при загрузке страницы
    function loadProfileData() {
        console.log('=== Loading profile data ===');
        
        const jsonField = document.getElementById('my_callsigns_json');
        if (!jsonField) {
            console.error('my_callsigns_json field not found!');
            return;
        }
        
        const rawData = jsonField.value.trim();
        console.log('Raw data from database:', rawData);
        
        if (!rawData || rawData === '[]') {
            console.log('No callsigns data found, adding empty field');
            addCallsign();
            return;
        }
        
        try {
            let callsigns;
            
            // Пытаемся распарсить как JSON
            try {
                callsigns = JSON.parse(rawData);
                console.log('Parsed callsigns:', callsigns);
            } catch (parseError) {
                console.log('Failed to parse as JSON, treating as simple list');
                // Если не JSON, возможно это простой список строк
                if (rawData.startsWith('[') && rawData.endsWith(']')) {
                    // Это JSON, но с ошибкой парсинга
                    callsigns = [];
                } else {
                    // Это простой список строк
                    callsigns = rawData.split(',').map(s => s.trim()).filter(s => s);
                }
            }
            
            // Очищаем контейнер
            const container = document.getElementById('callsigns-container');
            container.innerHTML = '';
            
            // Добавляем позывные в форму
            if (Array.isArray(callsigns)) {
                if (callsigns.length === 0) {
                    // Добавляем одно пустое поле
                    addCallsign();
                } else {
                    callsigns.forEach(function(callsign) {
                        let callsignValue = '';
                        
                        if (typeof callsign === 'object' && callsign.name) {
                            callsignValue = callsign.name;
                        } else if (typeof callsign === 'string') {
                            callsignValue = callsign;
                        }
                        
                        addCallsign(callsignValue);
                    });
                }
                
                console.log('Loaded callsigns into form');
            } else {
                console.error('Invalid callsigns data format:', callsigns);
                addCallsign();
            }
            
        } catch (error) {
            console.error('Error loading profile data:', error);
            addCallsign();
        }
    }
    
    // ========== Callsign Management Functions ==========
    
    // Initialize handlers for existing callsign inputs
    function initCallsignInputs() {
        document.querySelectorAll('.callsign-input').forEach(input => {
            input.addEventListener('input', function() {
                this.value = this.value.toUpperCase().replace(/[^A-Z0-9\\/]/g, '');
            });
        });
        console.log('Initialized callsign inputs');
    }

    // Add new callsign input
    function addCallsign(value = '') {
        const container = document.getElementById('callsigns-container');
        const item = document.createElement('div');
        item.className = 'my-callsign-item mb-2 d-flex';
        item.innerHTML = `
            <input type="text" class="form-control name-input callsign-input flex-grow-1 me-2"
                   name="my_callsigns_names[]"
                   value="${value}"
                   placeholder="Позывной"
                   autocomplete="off">
            <button type="button" class="btn btn-outline-danger btn-sm"
                    onclick="removeCallsign(this)">
                ✕
            </button>
        `;
        container.appendChild(item);
        
        // Инициализируем обработчики для нового поля
        initCallsignInputs();
        
        console.log('Added callsign input:', value);
    }

    // Remove callsign input
    function removeCallsign(button) {
        const container = document.getElementById('callsigns-container');
        const items = container.querySelectorAll('.my-callsign-item');
        
        if (items.length > 1) {
            // Удаляем элемент
            const item = button.closest('.my-callsign-item');
            item.remove();
            console.log('Removed callsign input, remaining:', items.length - 1);
        } else {
            // Если это последний элемент, просто очищаем его
            const item = button.closest('.my-callsign-item');
            const input = item.querySelector('input');
            input.value = '';
            console.log('Cleared last callsign input');
        }
    }
    
    // ========== Event Handlers ==========
    
    function initEventHandlers() {
        const form = document.getElementById('profile-edit-form');
        if (!form) {
            console.error('Profile form not found!');
            return;
        }
        
        // Form submit handler
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            console.log('=== DEBUG: Form Submit ===');
            console.log('Form submit triggered');
            
            const callsigns = [];
            const container = document.getElementById('callsigns-container');
            const items = container.querySelectorAll('.my-callsign-item');

            console.log('Found items:', items.length);
            
            items.forEach(function(item, index) {
                const input = item.querySelector('input[name="my_callsigns_names[]"]');
                if (input) {
                    const name = input.value.trim();
                    console.log(`Item ${index}: "${name}"`);
                    if (name) {
                        callsigns.push({
                            name: name.toUpperCase()
                        });
                    }
                }
            });

            console.log('Collected callsigns:', callsigns);
            
            const jsonField = document.getElementById('my_callsigns_json');
            if (jsonField) {
                const jsonValue = JSON.stringify(callsigns);
                jsonField.value = jsonValue;
                console.log('JSON field value set to:', jsonValue);
                
                // Debug: проверим, что данные действительно попали в поле
                console.log('JSON field after setting:', jsonField.value);
            } else {
                console.error('my_callsigns_json field not found!');
            }
            
            // Debug: проверим данные формы
            const formData = new FormData(form);
            console.log('Form data my_callsigns_json:', formData.get('my_callsigns_json'));
            
            // Показываем сообщение пользователю
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Сохранение...';
                submitBtn.disabled = true;
                
                // Восстанавливаем кнопку через 3 секунды
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 3000);
            }
            
            return false; // Предотвращаем отправку формы для тестирования
        });
        
        console.log('Event handlers initialized');
    }
    
    // ========== Global Functions ==========
    
    // Делаем функции глобально доступными для onclick атрибутов
    window.addCallsign = addCallsign;
    window.removeCallsign = removeCallsign;
    
    // ========== Initialize ==========
    
    // Инициализируем при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initProfileEdit);
    } else {
        initProfileEdit();
    }
    
})(jQuery);
'''
    
    return js_content

def main():
    """Основная функция"""
    print("=== СОЗДАНИЕ ИСПРАВЛЕННОГО JAVASCRIPT ФАЙЛА ===")
    
    # Создаем исправленный JavaScript
    js_content = fix_javascript()
    
    # Записываем в файл
    output_file = 'tlog/static/js/profile_edit_fixed.js'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✓ Исправленный JavaScript создан: {output_file}")
    
    # Также создаем резервную копию оригинального файла
    original_file = 'tlog/static/js/profile_edit.js'
    backup_file = 'tlog/static/js/profile_edit_backup.js'
    
    try:
        with open(original_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"✓ Резервная копия создана: {backup_file}")
    except Exception as e:
        print(f"⚠ Не удалось создать резервную копию: {e}")
    
    # Заменяем оригинальный файл
    try:
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✓ Оригинальный файл обновлен: {original_file}")
    except Exception as e:
        print(f"✗ Ошибка при обновлении файла: {e}")
    
    print("\n=== ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ ===")
    print("1. Замените в HTML шаблоне profile_edit.html:")
    print("   <script src='{% static 'js/profile_edit.js' %}'></script>")
    print("   на:")
    print("   <script src='{% static 'js/profile_edit_fixed.js' %}'></script>")
    print("")
    print("2. Или замените содержимое profile_edit.js на исправленную версию")
    print("")
    print("3. Перезапустите сервер и проверьте работу")

if __name__ == '__main__':
    main()