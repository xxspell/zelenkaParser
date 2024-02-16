import aiosqlite
from datetime import datetime

import settings

user_fields = settings.DB_USERFIELDS


class AsyncSQLiteDB:
    def __init__(self, db_path=settings.DB_PATH):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path)

        await self.create_table("comments", user_fields)

    async def disconnect(self):
        if self.conn:
            await self.conn.close()

    async def create_table(self, table_name, fields):
        # Check if the table is available
        check_table_query = (
            'SELECT name FROM sqlite_master WHERE type="table" AND name=?;'
        )
        result = await self.fetch_one(check_table_query, (table_name,))

        if not result:
            # The table doesn't exist, create it
            fields_str = ", ".join([" ".join(field) for field in fields])
            create_table_query = f"CREATE TABLE {table_name} ({fields_str});"
            await self.execute(create_table_query)

    async def execute(self, query, parameters=None):
        async with self.conn.execute(query, parameters or ()):
            await self.conn.commit()

    async def fetch_one(self, query, parameters=None):
        if self.conn:
            async with self.conn.execute(query, parameters or ()) as cursor:
                return await cursor.fetchone()
        else:
            print("No database connection.")

    async def fetch_all(self, query, parameters=None):
        if self.conn:
            async with self.conn.execute(query, parameters or ()) as cursor:
                return await cursor.fetchall()
        else:
            print("No database connection.")

    async def insert_comment(
        self,
        table_name,
        post_comment_id=None,
        post_id=None,
        comment_hide_text=None,
        comment_author=None,
        checked=None,
        error=None,
    ):
        date_add = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        columns = []
        values = []

        if post_comment_id is not None:
            columns.append("post_comment_id")
            values.append(post_comment_id)

        if post_id is not None:
            columns.append("post_id")
            values.append(post_id)

        if comment_hide_text is not None:
            columns.append("comment_hide_text")
            values.append(comment_hide_text)

        if comment_author is not None:
            columns.append("comment_author")
            values.append(comment_author)

        if checked is not None:
            columns.append("checked")
            values.append(checked)

        if error is not None:
            columns.append("error")
            values.append(error)

        columns.append("date_add")
        values.append(date_add)

        columns_str = ", ".join(columns)
        values_str = ", ".join(["?" for _ in values])

        insert_query = (
            f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});"
        )
        await self.execute(insert_query, values)

    async def update_row_by_id(self, table_name, update_values, row_id):
        update_columns = ", ".join([f"{key} = ?" for key in update_values.keys()])
        update_values_list = list(update_values.values())

        update_query = f"UPDATE {table_name} SET {update_columns} WHERE id = ?;"
        await self.execute(update_query, update_values_list + [row_id])
