import asyncio
import os, dotenv
from data import database, users, groups
from icecream import ic

ic.configureOutput(includeContext=True)

CONFIG: dict = dict()
ADMINS: list = []
GROUPS: list = []
QUERY: dict = {
    "sphere": "👷‍♂️ В какой сфере Вы работаете?",
    "type": "🧐 Что вы хотите продвигать на сайте?",
    "which_site": "📌 Какой сайт вам больше подходит?",
    "integration": "🔗 Требуется ли интеграция с другими сервисами?",
    "integration_input": "🛠 Введите названия сервиса, который хотите использовать",
    "info": "📊 Имеется ли информация по всем товарам в Excel/CSV файле?",
    "info_no": "📥 Сможете ли вы внести информацию в Excel-файл по нашей форме?",
    "billing": "💳 Нужно ли подключать оплату на сайте?(Только для юр.лиц)",
    "delivery": "🚚 Нужно ли подключать расчет стоимости доставки?(Только для юр.лиц)",
    "accounting": "📦 Нужно ли подключать интеграцию учета товаров на складе?",
    "example": "🔎 Есть ли пример сайта, на который можно ориентироваться или техническое задание?",
    "phone": "📞 Оставьте ваш номер телефона, чтобы менеджер мог с вами связаться."
}


async def main():
    global ADMINS, GROUPS
    await database.create_database()

    dotenv.load_dotenv()
    CONFIG['BOT_TOKEN'] = os.getenv('BOT_TOKEN')
    ADMINS.extend(await users.get_list_admin())
    GROUPS.extend(await groups.get_list_group_mailing())



asyncio.run(main())
