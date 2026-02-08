import telebot
from telebot import types
from disposables_data import DISPOSABLES
from liquids import LIQUIDS
import time
from urllib.parse import quote
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TOKEN = "8192143697:AAEd1nT-lrrsVmNn28lGLkNJK2b1mI-LoDs"
MANAGER = "manager_raznet"

BRANDS_PER_PAGE = 6
ITEMS_PER_PAGE = 6

bot = telebot.TeleBot(TOKEN)


# ================= SAFE EDIT =================
def safe_edit(call, text, kb=None):
    try:
        bot.edit_message_text(
            text=text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=kb
        )
    except telebot.apihelper.ApiTelegramException:
        pass


def order_link():
    text = "Здравствуйте! Хочу оформить заказ"
    return f"https://t.me/{MANAGER}?text={quote(text)}"


# ================= КАТАЛОГ (ТВОЙ) =================
catalog = {
    "💧 Жидкости": [
        {"name": "Жидкости", "desc": "Большой выбор брендов и вкусов"}
    ],

    "🔁 Картриджи": [
        {
            "name": "Vaporesso XROS (картриджи)",
            "desc": (
                "0.4 ohm • 3 ml\n"
                "0.6 ohm • 3 ml\n"
                "0.6 ohm • 2 ml\n"
                "0.8 ohm • 3 ml\n"
                "0.8 ohm • 2 ml\n\n"
                "💰 Цена: 300₽"
            )
        },
        {
            "name": "🔥 Испарители",
            "desc": (
                "🔹 Aegis Hero / Boost\n"
                "• GeekVape B 0.3 Coil\n"
                "• GeekVape B 0.4 Coil\n\n"
                "🔹 Pasito\n"
                "• K-1 — 4 шт\n\n"
                "💰 Цена: 300₽"
            )
        }
    ],

    "⚙️ Подсистемы": {
        "🕒 Предзаказ": [
            {
                "name": "📦 Подсистемы (предзаказ)",
                "desc": (
                    "🔹 Vaporesso\n"
                    "• XROS 5 Mini — 2550₽\n"
                    "• XROS 5 — 2950₽\n"
                    "• XROS PRO — 3100₽\n"
                    "• XROS PRO 2 — 3490₽\n"
                    "• XROS CUBE — 2300₽\n"
                    "• XROS Mini — 2220₽\n\n"
                    "🔹 GeekVape\n"
                    "• Aegis Hero 5 — 3290₽\n"
                    "• Aegis Boost LE — 2390₽\n\n"
                    "🚚 Доставка 2–3 дня"
                )
            }
        ],
        "✅ В наличии": [
            {
                "name": "📍 Подсистемы в наличии",
                "desc": (
                    "• XROS 5 Mini — 2550₽\n"
                    "• XROS 5 — 2950₽"
                )
            }
        ]
    },

    "🎁 Акции": [
        {"name": "Действующих акций на данный момент нет", "desc": ""}
    ]
}


# ================= START (ТВОЙ ТЕКСТ) =================
@bot.message_handler(commands=["start"])
def start(message):
    text = (
        "👋 Добро пожаловать в Raznet!\n\n"
        "У нас вы можете приобрести:\n"
        "• ⚙️ POD-системы\n"
        "• 💨 Одноразовые устройства\n"
        "• 💧 Жидкости\n"
        "• 🔋 Испарители и картриджи\n\n"
        "📦 Все товары в наличии, ассортимент обновляется.\n\n"
        "Выберите категорию:"
    )

    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("💧 Жидкости", callback_data="cat_liquids"),
        types.InlineKeyboardButton("🔥 Одноразки", callback_data="cat_disposables"),
        types.InlineKeyboardButton("🔁 Картриджи", callback_data="cat_cartridges"),
        types.InlineKeyboardButton("⚙️ Подсистемы", callback_data="cat_pods"),
        types.InlineKeyboardButton("🎁 Акции", callback_data="cat_sales"),
        types.InlineKeyboardButton("📞 Контакты", callback_data="contacts")
    )

    bot.send_message(message.chat.id, text, reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == "home")
def home(call):
    start(call.message)


# ================= ОДНОРАЗКИ =================
def open_disposables_brands(call, page):
    brands = list(DISPOSABLES.keys())
    start_idx = page * BRANDS_PER_PAGE
    end_idx = start_idx + BRANDS_PER_PAGE

    kb = types.InlineKeyboardMarkup(row_width=2)
    for i, brand in enumerate(brands[start_idx:end_idx], start=start_idx):
        kb.add(types.InlineKeyboardButton(brand, callback_data=f"dbrand_{i}_page_0"))

    if start_idx > 0:
        kb.add(types.InlineKeyboardButton("⬅️", callback_data=f"dbrands_page_{page-1}"))
    if end_idx < len(brands):
        kb.add(types.InlineKeyboardButton("➡️", callback_data=f"dbrands_page_{page+1}"))

    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    kb.add(types.InlineKeyboardButton("🏠 На главную", callback_data="home"))

    safe_edit(call, "🔥 Одноразки\nВыберите бренд:", kb)


@bot.callback_query_handler(func=lambda call: call.data.startswith("dbrands_page_"))
def dbrands_page(call):
    open_disposables_brands(call, int(call.data.split("_")[2]))


def open_disposable_brand(call, bi, page):
    brand = list(DISPOSABLES.keys())[bi]
    models = list(DISPOSABLES[brand].keys())

    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    kb = types.InlineKeyboardMarkup(row_width=1)
    for i, model in enumerate(models[start:end], start=start):
        kb.add(types.InlineKeyboardButton(model, callback_data=f"dmodel_{bi}_{i}"))

    if start > 0:
        kb.add(types.InlineKeyboardButton("⬅️", callback_data=f"dbrand_{bi}_page_{page-1}"))
    if end < len(models):
        kb.add(types.InlineKeyboardButton("➡️", callback_data=f"dbrand_{bi}_page_{page+1}"))

    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="cat_disposables"))
    kb.add(types.InlineKeyboardButton("🏠 На главную", callback_data="home"))

    safe_edit(call, f"{brand}\nВыберите модель:", kb)


@bot.callback_query_handler(func=lambda call: call.data.startswith("dbrand_"))
def dbrand_handler(call):
    _, bi, _, page = call.data.split("_")
    open_disposable_brand(call, int(bi), int(page))


@bot.callback_query_handler(func=lambda call: call.data.startswith("dmodel_"))
def open_disposable_model(call):
    _, bi, mi = call.data.split("_")
    brand = list(DISPOSABLES.keys())[int(bi)]
    model = list(DISPOSABLES[brand].keys())[int(mi)]
    item = DISPOSABLES[brand][model]

    text = f"🔥 {brand}\n📦 {model}\n\n🍓 Вкусы:\n{item['flavors']}\n💰 Цена: {item['price']}"

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🛒 Заказать", url=order_link()))
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"dbrand_{bi}_page_0"))
    kb.add(types.InlineKeyboardButton("🏠 На главную", callback_data="home"))

    safe_edit(call, text, kb)


# ================= КАТЕГОРИИ =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def open_category(call):
    key = call.data.replace("cat_", "")

    if key == "disposables":
        open_disposables_brands(call, 0)
        return

    if key == "liquids":
        open_liquid_brands(call, 0)
        return

    if key == "pods":
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("🕒 Предзаказ", callback_data="pods_pre"))
        kb.add(types.InlineKeyboardButton("✅ В наличии", callback_data="pods_yes"))
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))
        kb.add(types.InlineKeyboardButton("🏠 На главную", callback_data="home"))
        safe_edit(call, "⚙️ Подсистемы\nВыберите статус:", kb)
        return

    mapping = {
        "cartridges": "🔁 Картриджи",
        "sales": "🎁 Акции"
    }

    category = mapping[key]
    items = catalog[category]

    text = f"{category}\n\n"
    for item in items:
        text += f"• {item['name']}\n{item['desc']}\n\n"

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🛒 Заказать", url=order_link()))
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    kb.add(types.InlineKeyboardButton("🏠 На главную", callback_data="home"))

    safe_edit(call, text, kb)


# ================= ПОДСИСТЕМЫ =================
@bot.callback_query_handler(func=lambda call: call.data in ["pods_pre", "pods_yes"])
def open_pods(call):
    key = "🕒 Предзаказ" if call.data == "pods_pre" else "✅ В наличии"
    items = catalog["⚙️ Подсистемы"][key]

    text = f"⚙️ Подсистемы • {key}\n\n"
    for item in items:
        text += f"• {item['name']}\n{item['desc']}\n\n"

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🛒 Заказать", url=order_link()))
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="cat_pods"))
    kb.add(types.InlineKeyboardButton("🏠 На главную", callback_data="home"))

    safe_edit(call, text, kb)


# ================= ЖИДКОСТИ =================
def open_liquid_brands(call, page):
    brands = list(LIQUIDS.keys())
    start = page * BRANDS_PER_PAGE
    end = start + BRANDS_PER_PAGE

    kb = types.InlineKeyboardMarkup(row_width=2)
    for i, brand in enumerate(brands[start:end], start=start):
        kb.add(types.InlineKeyboardButton(brand, callback_data=f"lbrand_{i}_page_0"))

    if start > 0:
        kb.add(types.InlineKeyboardButton("⬅️", callback_data=f"lbrands_page_{page-1}"))
    if end < len(brands):
        kb.add(types.InlineKeyboardButton("➡️", callback_data=f"lbrands_page_{page+1}"))

    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    kb.add(types.InlineKeyboardButton("🏠 На главную", callback_data="home"))

    safe_edit(call, "💧 Жидкости\nВыберите бренд:", kb)


@bot.callback_query_handler(func=lambda call: call.data.startswith("lbrands_page_"))
def lbrands_page(call):
    open_liquid_brands(call, int(call.data.split("_")[2]))


def open_liquid_brand(call, bi, page):
    brand = list(LIQUIDS.keys())[bi]
    lines = list(LIQUIDS[brand].keys())

    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE

    kb = types.InlineKeyboardMarkup(row_width=1)
    for i, line in enumerate(lines[start:end], start=start):
        kb.add(types.InlineKeyboardButton(line, callback_data=f"lline_{bi}_{i}"))

    if start > 0:
        kb.add(types.InlineKeyboardButton("⬅️", callback_data=f"lbrand_{bi}_page_{page-1}"))
    if end < len(lines):
        kb.add(types.InlineKeyboardButton("➡️", callback_data=f"lbrand_{bi}_page_{page+1}"))

    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="cat_liquids"))
    kb.add(types.InlineKeyboardButton("🏠 На главную", callback_data="home"))

    safe_edit(call, f"{brand}\nВыберите линейку:", kb)


@bot.callback_query_handler(func=lambda call: call.data.startswith("lbrand_"))
def lbrand_handler(call):
    _, bi, _, page = call.data.split("_")
    open_liquid_brand(call, int(bi), int(page))


@bot.callback_query_handler(func=lambda call: call.data.startswith("lline_"))
def open_liquid_line(call):
    _, bi, li = call.data.split("_")
    brand = list(LIQUIDS.keys())[int(bi)]
    line = list(LIQUIDS[brand].keys())[int(li)]
    item = LIQUIDS[brand][line]

    flavors = ""
    for name, ok in item["flavors"].items():
        flavors += f"{'✅' if ok else '❌'} {name}\n"

    text = (
        f"💧 {brand}\n"
        f"📦 {line}\n\n"
        f"🍓 Вкусы:\n{flavors}\n"
        f"💰 Цена: {item['price']}₽"
    )

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🛒 Заказать", url=order_link()))
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"lbrand_{bi}_page_0"))
    kb.add(types.InlineKeyboardButton("🏠 На главную", callback_data="home"))

    safe_edit(call, text, kb)


# ================= КОНТАКТЫ =================
@bot.callback_query_handler(func=lambda call: call.data == "contacts")
def contacts(call):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🛒 Заказать", url=order_link()))
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    kb.add(types.InlineKeyboardButton("🏠 На главную", callback_data="home"))

    safe_edit(call, "👤 Менеджер: @manager_raznet\n🕘 Работаем ежедневно", kb)


@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    start(call.message)


if __name__ == "__main__":
    logger.info("🤖 Запускаю Telegram бота...")
    logger.info(f"⚙️ Токен: {'установлен' if TOKEN else 'не найден'}")

    # Запускаем с автоматическим перезапуском
    while True:
        try:
            logger.info("🚀 Бот запущен и ожидает сообщений...")
            bot.polling(none_stop=True, interval=1, timeout=60)
        except Exception as e:
            logger.error(f"⚠️ Ошибка: {e}")
            logger.info("🔄 Перезапуск через 10 секунд...")
            time.sleep(10)