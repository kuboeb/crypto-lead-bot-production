"""
Добавляет трекинг в хендлеры бота
"""
import re

# Читаем файл
with open('app/handlers.py', 'r') as f:
    content = f.read()

# Добавляем импорт
if 'from app.analytics.tracker import ActionTracker' not in content:
    import_line = 'from app.database.models import'
    content = content.replace(
        import_line,
        f'{import_line}\nfrom app.analytics.tracker import ActionTracker'
    )

# Добавляем трекинг в start команду
start_pattern = r'@dp\.message\(Command\("start"\)\)\nasync def start_command.*?:'
start_replacement = '''@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды /start"""
    await ActionTracker.track_action(
        message.from_user,
        "start",
        message.text,
        "funnel_start"
    )'''

content = re.sub(
    r'@dp\.message\(Command\("start"\)\)\nasync def start_command.*?:',
    start_replacement,
    content,
    flags=re.MULTILINE | re.DOTALL,
    count=1
)

# Добавляем трекинг в кнопку "Записаться"
apply_pattern = r'text="Записаться на бесплатное обучение".*?\n.*?await callback\.answer\(\)'
if 'await ActionTracker.track_action' not in content:
    content = re.sub(
        apply_pattern,
        lambda m: m.group(0) + '\n    await ActionTracker.track_action(callback.from_user, "button_click", "apply", "funnel_apply_clicked")',
        content,
        flags=re.MULTILINE | re.DOTALL
    )

# Сохраняем
with open('app/handlers.py', 'w') as f:
    f.write(content)

print("✅ Трекинг добавлен в хендлеры")
