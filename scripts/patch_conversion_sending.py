"""
Добавляет автоматическую отправку конверсий
"""
import re

# Читаем файл
with open('app/handlers/application_handler.py', 'r') as f:
    content = f.read()

# Добавляем импорт
if 'from app.services.conversion_sender import ConversionSender' not in content:
    import_line = 'from app.database.models import'
    content = content.replace(
        import_line,
        f'{import_line}\nfrom app.services.conversion_sender import ConversionSender'
    )

# Находим место после сохранения заявки
save_pattern = r'await session\.commit\(\)\s*await callback\.message\.answer'
if 'ConversionSender.send_conversion' not in content:
    replacement = '''await session.commit()
        
        # Отправляем конверсию в рекламную сеть
        asyncio.create_task(ConversionSender.send_conversion(application.id))
        
        await callback.message.answer'''
    
    content = re.sub(save_pattern, replacement, content)

# Сохраняем
with open('app/handlers/application_handler.py', 'w') as f:
    f.write(content)

print("✅ Автоматическая отправка конверсий добавлена")
