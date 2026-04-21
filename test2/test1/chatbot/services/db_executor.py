"""
Модуль выполнения SQL-запросов к базе данных завода.
"""
import sqlite3
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class DBExecutor:
    """Выполняет SQL-запросы к factory database."""

    def __init__(self):
        self.db_path = settings.FACTORY_DB_PATH

    def execute(self, sql: str) -> dict:
        """
        Выполнить SQL-запрос и вернуть результаты.
        
        Args:
            sql: SQL-запрос (только SELECT)
        
        Returns:
            dict: {
                'success': bool,
                'columns': list,
                'rows': list of dicts,
                'count': int,
                'error': str or None
            }
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(sql)
            rows = cursor.fetchall()

            if rows:
                columns = [description[0] for description in cursor.description]
                result_rows = [dict(row) for row in rows]
            else:
                columns = [description[0] for description in cursor.description] if cursor.description else []
                result_rows = []

            conn.close()

            return {
                'success': True,
                'columns': columns,
                'rows': result_rows,
                'count': len(result_rows),
                'error': None,
            }

        except sqlite3.Error as e:
            logger.error(f"Ошибка выполнения SQL: {e}\nSQL: {sql}")
            return {
                'success': False,
                'columns': [],
                'rows': [],
                'count': 0,
                'error': f"Ошибка базы данных: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}\nSQL: {sql}")
            return {
                'success': False,
                'columns': [],
                'rows': [],
                'count': 0,
                'error': f"Ошибка: {str(e)}",
            }

    def get_schema_summary(self) -> str:
        """Получить краткую сводку о таблицах в БД."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]

            schema_info = []
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [row[1] for row in cursor.fetchall()]
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                schema_info.append(f"{table} ({count} записей): {', '.join(columns[:10])}...")

            conn.close()
            return "\n".join(schema_info)
        except Exception as e:
            return f"Ошибка получения схемы: {e}"


# Singleton
db_executor = DBExecutor()
