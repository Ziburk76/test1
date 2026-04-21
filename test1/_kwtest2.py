import sys
sys.path.insert(0, '.')
from chatbot.services.semantic_layer import KEYWORD_TABLE_MAP, get_tables_for_question

f = open('kw_test2.txt', 'w', encoding='utf-8')

# Тест: ищем "станок" в вопросе
q = 'Какие станки есть на заводе'
ql = q.lower()
f.write(f'Question: {q}\n')
f.write(f'Lower: {ql}\n')
f.write(f'"станок" in ql: {"станок" in ql}\n')
f.write(f'"станк" in ql: {"станк" in ql}\n')
f.write(f'"станки" in ql: {"станки" in ql}\n')

# Пробуем найти
for kw in ['станок', 'станк', 'станки', 'машин']:
    if kw in ql:
        f.write(f'MATCHED: "{kw}"\n')

tables, keywords = get_tables_for_question(q)
f.write(f'Tables: {sorted(tables)}\n')
f.write(f'Keywords: {keywords}\n')

f.close()
print('Done')
