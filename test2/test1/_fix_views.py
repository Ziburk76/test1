import re

with open('chatbot/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the answer generation part
pattern = r"# Генерируе[^\n]+\n\s+if error:\n\s+answer = f.*?\n\s+elif db_result.*?\n\s+answer = answer_generator\.generate.*?\n\s+else:\n\s+answer = .*"

replacement = """# Генерируем ответ (без LLM - для скорости)
        if error:
            answer = f'Ошибка: {error}'
        elif db_result and db_result.get('success'):
            count = db_result.get('count', 0)
            cols = ', '.join(db_result.get('columns', []))
            answer = f'Получено {count} записей. Колонки: {cols}. Результат в таблице ниже.'
        else:
            answer = 'Данных не найдено.'"""

result = re.sub(pattern, replacement, content, flags=re.DOTALL)

if result != content:
    with open('chatbot/views.py', 'w', encoding='utf-8') as f:
        f.write(result)
    print('Replaced successfully')
else:
    print('No match found, trying line-by-line')
    lines = content.split('\n')
    new_lines = []
    skip_until_else = False
    for i, line in enumerate(lines):
        if 'answer_generator.generate' in line:
            skip_until_else = False
            new_lines.append("            count = db_result.get('count', 0)")
            new_lines.append("            cols = ', '.join(db_result.get('columns', []))")
            new_lines.append("            answer = f'Получено {count} записей. Колонки: {cols}. Результат в таблице ниже.'")
            print(f'Replaced line {i+1}')
        else:
            new_lines.append(line)
    
    with open('chatbot/views.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print('Done')
