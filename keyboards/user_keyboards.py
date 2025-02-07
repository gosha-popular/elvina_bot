from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

KEYBOARDS = {
    "accounting": ['✅ Да', '❌ Нет'],
    "billing": ['✅ Да', '❌ Нет'],
    "delivery": ['✅ Да', '❌ Нет'],
    "example": ['✅ Да', '❌ Нет'],
    "info": ['✅ Да', '❌ Нет'],
    "info_no": ['✅ Да', '❌ Нет'],
    "integration": ['✅ Да', '❌ Нет'],
    "sphere": ["🏗 Строительство",
               "🏠 Ремонтные работы",
               "🏭 Промышленность",
               "🚗 Автомобили",
               "💄 Бьюти-сфера",
               "👨‍💻 Специалисты",
               "🍕 Еда и товары"],
    "type": ["🏷 Товары",
             "🎭 Услуги"],
    "which_site": ["🔹 Одностраничный",
         "🔹 Многостраничный",
         "🔹 Каталог товаров",
         "🔹 Интернет-магазин",
         "🔹 Не знаю, нужна консультация"]
}




async def get_keyboards(state: str) -> InlineKeyboardMarkup | None:
    lst = KEYBOARDS.get(state, []).copy()
    lst.append('🏠 Вернуться в главное меню')
    grid = [(1,), (2, 1)][len(lst) == 3]
    keyboard = await build_inline_keyboard(lst, grid)
    return keyboard


async def build_inline_keyboard(button_names: list, grid: tuple | None = None) -> InlineKeyboardMarkup | None:
    builder = InlineKeyboardBuilder()
    for name in button_names:
        builder.add(InlineKeyboardButton(text=name, callback_data=name))
    if grid:
        builder.adjust(*grid)
    else:
        builder.adjust(1)

    return builder.as_markup()
