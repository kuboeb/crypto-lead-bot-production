"""
Очистка импортов удаленных моделей
"""
import os
import re

# Модели, которые были удалены
removed_models = ['PostbackLog', 'UserAction', 'FunnelSnapshot', 'BuyerPixelConfig', 'AdminUser']

def clean_file(filepath):
    """Очищает файл от импортов удаленных моделей"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Удаляем из импортов
    for model in removed_models:
        # Различные варианты импорта
        content = re.sub(rf',\s*{model}', '', content)
        content = re.sub(rf'{model}\s*,', '', content)
        content = re.sub(rf'\s*{model}\s*', '', content)
    
    # Удаляем пустые импорты
    content = re.sub(r'from app.database.models import\s*\n', '', content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Очищен файл: {filepath}")

# Проходим по всем Python файлам
for root, dirs, files in os.walk('app'):
    # Пропускаем __pycache__
    if '__pycache__' in root:
        continue
    
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            clean_file(filepath)

print("\n✅ Очистка завершена")
