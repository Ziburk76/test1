import sys
sys.path.insert(0, '.')
from chatbot.services.semantic_layer import KEYWORD_TABLE_MAP, get_tables_for_question

f = open('kw_test.txt', 'w', encoding='utf-8')
f.write(f'Map keys: {len(KEYWORD_TABLE_MAP)}\n')

questions = [
    'простои станков',
    'Покажи простои станков',
    'Какие станки есть на заводе',
    'Кто работал на станках',
    'Покажи расписание работы станков',
    'Покажи нарушения контроля',
    'аналитика по цеху',
]

for q in questions:
    tables, keywords = get_tables_for_question(q)
    f.write(f'\nQ: {q}\n')
    f.write(f'  Tables ({len(tables)}): {sorted(tables)}\n')
    f.write(f'  Keywords: {keywords}\n')

f.close()
print('Done')
