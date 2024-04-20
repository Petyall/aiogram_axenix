import aiosqlite


async def connect_to_db():
    db_connection = await aiosqlite.connect('database.db')
    return db_connection


# Создание таблиц
async def create_users_table():
    db = await connect_to_db()
    async with db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)")
        await db.commit()
    await db.close()


async def create_slides_table():
    db = await connect_to_db()
    async with db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS slides (id INTEGER PRIMARY KEY, image TEXT, description TEXT)")
        await db.commit()
    await db.close()


async def create_messages_table():
    db = await connect_to_db()
    async with db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, user_id TEXT)")
        await db.commit()
    await db.close()


# Добавление записей
async def insert_message(message_id, user_id):
    db = await connect_to_db()
    async with db.cursor() as cursor:
        try:
            await cursor.execute("INSERT INTO messages (id, user_id) VALUES (?, ?)", (message_id, user_id))
            await db.commit()
        except aiosqlite.IntegrityError:
            print(f"Сообщение {message_id} уже зарегистрировано")
    await db.close()


async def insert_user(user_id, username):
    db = await connect_to_db()
    async with db.cursor() as cursor:
        try:
            await cursor.execute("INSERT INTO users (id, username) VALUES (?, ?)", (user_id, username))
            await db.commit()
        except aiosqlite.IntegrityError:
            print(f"Пользователь {user_id} уже зарегистрирован")
    await db.close()


async def insert_slide(image, description):
    db = await connect_to_db()
    async with db.cursor() as cursor:
        try:
            await cursor.execute("INSERT INTO slides (image, description) VALUES (?, ?)", (image, description))
            await db.commit()
        except:
            print("Непредвиденная ошибка")
    await db.close()


# Получение записей
async def get_slide(slide_id):
    db = await connect_to_db()
    async with db.execute("SELECT * FROM slides WHERE id = ?", (slide_id,)) as cursor:
        result = await cursor.fetchone()
    await db.close()
    return result


async def get_max_slide_id():
    db = await connect_to_db()
    async with db.execute("SELECT MAX(id) FROM slides") as cursor:
        result = await cursor.fetchone()
    await db.close()
    return int(result[0])


async def get_users():
    db = await connect_to_db()
    async with db.execute("SELECT id FROM users") as cursor:
        result = await cursor.fetchall()
    await db.close()
    return [int(user[0]) for user in result]


async def get_messages():
    db = await connect_to_db()
    async with db.execute("SELECT * FROM messages") as cursor:
        result = await cursor.fetchall()
    await db.close()
    return result


# Удаление записей
async def delete_messages():
    db = await connect_to_db()
    async with db.cursor() as cursor:
        try:
            # await cursor.execute("TRUNCATE TABLE messages")
            await cursor.execute("DELETE FROM messages")
            await db.commit()
        except:
            print(f"Неожиданная ошибка при очистке таблицы messages")
    await db.close()










