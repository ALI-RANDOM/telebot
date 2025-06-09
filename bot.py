import os
import logging
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from commands.currency import (
    currency_message_handler,
    give_handler,
    subtract_handler,
    balance_handler
)

# =====================================
# إعدادات البوت (التوكن ثابتًا)
# =====================================
BOT_TOKEN = "7358926740:AAGfwIacwgrVHcueGyMvV0ftBSlTXPu1kJ4"

# =====================================
# الرابط الخارجي الثابت (الـURL الذي أعطاه Render)
# =====================================
EXTERNAL_URL = "https://telebot-8o93.onrender.com"
WEBHOOK_URL = f"{EXTERNAL_URL}/{BOT_TOKEN}"

# =====================================
# إعداد نظام التسجيل
# =====================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =====================================
# بيانات الروابط والأزرار
# =====================================
ALL_BUTTONS = [
    ("💰 الأجر", "https://t.me/Ibrhaimp"),
    ("🧑‍💼 الدعم", "https://t.me/Hell_supportbot"),
    ("📤 التوزيع", "https://t.me/+sP1KiRwb07ViYWNk"),
    ("📌 القوانين", "https://t.me/+1BUMvsFtRc00MGQ8"),
    ("🎯 المهام", "https://t.me/+LK8rr9LJXk1kYmE0"),
    ("🧾 الوصف", "https://t.me/HELL_GTA"),
    ("🔗 رتب", "https://t.me/+RiPkO-JHXt9iMTZi"),
    (
        "🎮 رابط كلان هيل",
        "https://socialclub.rockstargames.com/crew/the_best_colors_to_u/wall",
    ),
]

# =====================================
# تعريف الأوامر مع قائمة المرادفات لكل زر
# =====================================
BUTTONS_DATA = [
    {
        "keywords": ["قوانين", "القوانين"],
        "text": "📌 القوانين",
        "url": "https://t.me/+1BUMvsFtRc00MGQ8",
        "message": "إليك رابط القوانين"
    },
    {
        "keywords": ["مهام", "المهام"],
        "text": "🎯 المهام",
        "url": "https://t.me/+LK8rr9LJXk1kYmE0",
        "message": "إليك رابط المهام"
    },
    {
        "keywords": ["كلان", "الكلان"],
        "text": "🎮 رابط كلان هيل",
        "url": "https://socialclub.rockstargames.com/crew/the_best_colors_to_u/wall",
        "message": "إليك رابط الكلان"
    },
    {
        "keywords": ["توزيع", "التوزيع", "توزيعات"],
        "text": "📤 التوزيع",
        "url": "https://t.me/+sP1KiRwb07ViYWNk",
        "message": "إليك رابط التوزيع"
    },
    {
        "keywords": ["وصف", "الوصف"],
        "text": "🧾 الوصف",
        "url": "https://t.me/HELL_GTA",
        "message": "إليك رابط الوصف"
    },
    {
        "keywords": ["دعم", "الدعم"],
        "text": "🧑‍💼 الدعم",
        "url": "https://t.me/Hell_supportbot",
        "message": "إليك رابط الدعم"
    },
    {
        "keywords": ["أجر", "اجر", "راتب"],
        "text": "💰 الأجر",
        "url": "https://t.me/Ibrhaimp",
        "message": "إليك رابط الأجر"
    },
    {
        "keywords": ["رتب", "رتبه", "الرتبه"],
        "text": "🔗 رتب",
        "url": "https://t.me/+RiPkO-JHXt9iMTZi",
        "message": "إليك رابط الرتب"
    },
]

# =====================================
# رابط الصورة عند القفل/الفتح
# =====================================
LOCK_IMAGE_URL = "https://i.postimg.cc/Mcsv2bz9/lock-image.jpg"

# =====================================
# متغيرات المراقبة (مثلاً لعدد التحذيرات)
# =====================================
warnings_counter = {}  # هيكل: {chat_id: {user_id: warning_count}}

# =====================================
# دوال التحقق من صلاحيات المشرفين
# =====================================
async def is_user_admin(update: Update, user_id: int) -> bool:
    """يتحقق إن كان user_id مشرفًا أو مالكًا في هذه المجموعة."""
    try:
        member = await update.effective_chat.get_member(user_id)
        return member.status in ("administrator", "creator")
    except Exception as e:
        logger.error(f"فشل في جلب صلاحيات المستخدم {user_id}: {e}")
        return False

# =====================================
# دوال الأوامر الأساسية
# =====================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البدء /start"""
    user = update.effective_user
    logger.info(f"أمر /start من المستخدم: {user.first_name} (ID: {user.id})")
    
    welcome_message = (
        f"🔥 مرحباً {user.mention_html()}! أنا بوت كلان هيل\n\n"
        "📋 الكلمات المتاحة:\n"
        "• قوانين → رابط القوانين\n"
        "• مهام → رابط المهام\n"
        "• كلان → رابط الكلان\n"
        "• توزيع → رابط التوزيع\n"
        "• وصف → رابط الوصف\n"
        "• دعم → رابط الدعم\n"
        "• أجر → رابط الأجر\n"
        "• رتب → رابط رتب\n"
        "• هيل → جميع الروابط\n\n"
        "💡 اكتب أي كلمة من هذه الكلمات (بما فيها المرادفات) وسأعطيك الرابط المطلوب!"
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode="HTML"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المساعدة /help"""
    user = update.effective_user
    logger.info(f"أمر /help من المستخدم: {user.id}")
    
    keyboard = []
    for button_text, button_url in ALL_BUTTONS:
        keyboard.append([InlineKeyboardButton(button_text, url=button_url)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🔥 مرحباً {user.mention_html()}، اختر الرابط المطلوب 👇",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل النصية الأساسية"""
    message = update.message
    user = update.effective_user
    chat = update.effective_chat
    text = message.text.lower().strip()
    
    logger.info(f"رسالة من {user.first_name} (ID: {user.id}) في {chat.type}: {message.text}")
    
    # إذا كانت الرسالة تساوي كلمة "هيل" بالضبط
    if text == "هيل":
        keyboard = []
        for button_text, button_url in ALL_BUTTONS:
            keyboard.append([InlineKeyboardButton(button_text, url=button_url)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(
            f"تفضل يا عسل {user.mention_html()}، هذه قائمة جميع الروابط المتاحة 👇",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        return
    
    # إذا كانت الرسالة تطابق أي كلمة مفردة من BUTTONS_DATA
    for entry in BUTTONS_DATA:
        for kw in entry["keywords"]:
            if text == kw:
                keyboard = [[InlineKeyboardButton(entry["text"], url=entry["url"])]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await message.reply_text(
                    f"{entry['message']} يا عسل {user.mention_html()} 👤",
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
                return
    
    # اختبار البوت (إذا كانت الرسالة تساوي "تست" أو "test" أو "اختبار")
    if text in ["تست", "test", "اختبار"]:
        await message.reply_text(f"✅ البوت يعمل بشكل ممتاز، تفضل {user.mention_html()}!")
        return

# =====================================
# دوال أوامر المشرفين
# =====================================
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /ban
    يحظر المستخدم المجيب على رسالته. للمشرفين فقط.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not await is_user_admin(update, user.id):
        await message.reply_text("📛 أنت لست مشرفًا في القروب تكرار الامر قد يعرضك للكتم.")
        return

    if not message.reply_to_message:
        await message.reply_text("❌ يرجى الرد على رسالة المستخدم الذي تريد حظره.")
        return

    target = message.reply_to_message.from_user
    if await is_user_admin(update, target.id):
        await message.reply_text("❌ لا يمكنك حظر مشرف أو مالك.")
        return

    try:
        await context.bot.ban_chat_member(chat.id, target.id)
        await message.reply_text(f"☑️ تم حظر المستخدم {target.first_name} (ID: {target.id})")
        logger.info(f"تم حظر {target.id} بأمر من {user.id} في دردشة {chat.id}")
    except Exception as e:
        logger.error(f"خطأ أثناء حظر المستخدم: {e}")
        await message.reply_text("❌ حدث خطأ أثناء محاولة الحظر.")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /unban
    يرفع الحظر عن المستخدم المجيب على رسالته أو المحدد بالمعرّف. للمشرفين فقط.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not await is_user_admin(update, user.id):
        await message.reply_text("📛 أنت لست مشرفًا في القروب تكرار الامر قد يعرضك للكتم.")
        return

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        if context.args and context.args[0].isdigit():
            target_id = int(context.args[0])
            member_obj = await context.bot.get_chat_member(chat.id, target_id)
            target = member_obj.user
        else:
            await message.reply_text("❌ يرجى الرد على رسالة المستخدم أو ذكر المعرف لرفع الحظر.")
            return

    try:
        await context.bot.unban_chat_member(chat.id, target.id)
        await message.reply_text(f"☑️ تم رفع الحظر عن المستخدم {target.first_name} (ID: {target.id})")
        logger.info(f"تم رفع الحظر عن {target.id} بأمر من {user.id} في دردشة {chat.id}")
    except Exception as e:
        logger.error(f"خطأ أثناء رفع الحظر: {e}")
        await message.reply_text("❌ حدث خطأ أثناء محاولة رفع الحظر.")

async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /kick
    يطرد المستخدم المجيب على رسالته (حظر ثم رفع الحظر). للمشرفين فقط.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not await is_user_admin(update, user.id):
        await message.reply_text("📛 أنت لست مشرفًا في القروب تكرار الامر قد يعرضك للكتم.")
        return

    if not message.reply_to_message:
        await message.reply_text("❌ يرجى الرد على رسالة المستخدم الذي تريد طرده.")
        return

    target = message.reply_to_message.from_user
    if await is_user_admin(update, target.id):
        await message.reply_text("❌ لا يمكنك طرد مشرف أو مالك.")
        return

    try:
        await context.bot.ban_chat_member(chat.id, target.id)
        await context.bot.unban_chat_member(chat.id, target.id)
        await message.reply_text(f"🚫 تم طرد المستخدم {target.first_name} (ID: {target.id})")
        logger.info(f"تم طرد {target.id} بأمر من {user.id} في دردشة {chat.id}")
    except Exception as e:
        logger.error(f"خطأ أثناء طرد المستخدم: {e}")
        await message.reply_text("❌ حدث خطأ أثناء محاولة الطرد.")

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /mute
    يكتم المستخدم المجيب على رسالته: عدم إرسال رسائل فقط. للمشرفين فقط.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not await is_user_admin(update, user.id):
        await message.reply_text("📛 أنت لست مشرفًا في القروب تكرار الامر قد يعرضك للكتم.")
        return

    if not message.reply_to_message:
        await message.reply_text("❌ يرجى الرد على رسالة المستخدم الذي تريد كتمه.")
        return

    target = message.reply_to_message.from_user
    if await is_user_admin(update, target.id):
        await message.reply_text("❌ لا يمكنك كتم مشرف أو مالك.")
        return

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat.id,
            user_id=target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.reply_text(f"🔇 تم كتم المستخدم {target.first_name} (ID: {target.id})")
        logger.info(f"تم كتم {target.id} بأمر من {user.id} في دردشة {chat.id}")
    except Exception as e:
        logger.error(f"خطأ أثناء كتم المستخدم: {e}")
        await message.reply_text("❌ حدث خطأ أثناء محاولة الكتم.")

async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /unmute
    يرفع الكتم عن المستخدم المجيب على رسالته. للمشرفين فقط.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not await is_user_admin(update, user.id):
        await message.reply_text("📛 أنت لست مشرفًا في القروب تكرار الامر قد يعرضك للكتم.")
        return

    if not message.reply_to_message:
        await message.reply_text("❌ يرجى الرد على رسالة المستخدم الذي تريد رفع الكتم عنه.")
        return

    target = message.reply_to_message.from_user
    if await is_user_admin(update, target.id):
        await message.reply_text("❌ لا يمكن رفع الكتم عن مشرف أو مالك.")
        return

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat.id,
            user_id=target.id,
            permissions=ChatPermissions(can_send_messages=True)
        )
        await message.reply_text(f"🔊 تم رفع الكتم عن المستخدم {target.first_name} (ID: {target.id})")
        logger.info(f"تم رفع الكتم عن {target.id} بأمر من {user.id} في دردشة {chat.id}")
    except Exception as e:
        logger.error(f"خطأ أثناء رفع الكتم: {e}")
        await message.reply_text("❌ حدث خطأ أثناء محاولة رفع الكتم.")

async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /warn
    يضيف تحذيرًا للمستخدم (الرد على رسالته). بعد 3 تحذيرات يتم كتمه تلقائيًا.
    للمشرفين فقط.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not await is_user_admin(update, user.id):
        await message.reply_text("📛 أنت لست مشرفًا في القروب تكرار الامر قد يعرضك للكتم.")
        return

    if not message.reply_to_message:
        await message.reply_text("❌ يرجى الرد على رسالة المستخدم الذي تريد تحذيره.")
        return

    target = message.reply_to_message.from_user
    if await is_user_admin(update, target.id):
        await message.reply_text("❌ لا يمكن تحذير مشرف أو مالك.")
        return

    chat_warnings = warnings-counter.setdefault(chat.id, {})
    count = chat_warnings.get(target.id, 0) + 1
    chat_warnings[target.id] = count

    try:
        if count >= 3:
            await context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=target.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await message.reply_text(
                f"⚠️ تم إرسال التحذير الثالث للمستخدم {target.first_name}.\n"
                f"🚫 لذلك، تم كتمه مؤقتًا لمدة ثلاث أيام."
            )
            chat_warnings[target.id] = 0

            async def unmute_after_delay():
                await asyncio.sleep(259200)  # 3 أيام بالثواني
                try:
                    await context.bot.restrict_chat_member(
                        chat_id=chat.id,
                        user_id=target.id,
                        permissions=ChatPermissions(can_send_messages=True)
                    )
                    await context.bot.send_message(
                        chat_id=chat.id,
                        text=f"🔊 تم رفع الكتم تلقائيًا عن {target.first_name} بعد انتهاء المهلة."
                    )
                    logger.info(f"رفع الكتم تلقائيًا عن {target.id} بعد التحذير الثالث.")
                except Exception as e:
                    logger.error(f"خطأ أثناء رفع الكتم بعد انتهاء المهلة: {e}")

            context.application.create_task(unmute_after_delay())

        else:
            await message.reply_text(
                f"⚠️ تم تحذير المستخدم {target.first_name}. "
                f"هذه هي التحذير رقم {count} من 3."
            )
            logger.info(f"تم تحذير {target.id} (العدد: {count}) بأمر من {user.id} في دردشة {chat.id}")
    except Exception as e:
        logger.error(f"خطأ أثناء تنفيذ أمر warn: {e}")
        await message.reply_text("❌ حدث خطأ أثناء محاولة التحذير.")

async def clearwarn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /clearwarn
    يزيل جميع التحذيرات من المستخدم المردود عليه أو المحدد بالمعرّف.
    للمشرفين فقط.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not await is_user_admin(update, user.id):
        await message.reply_text("📛 أنت لست مشرفًا في القروب تكرار الامر قد يعرضك للكتم.")
        return

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        if context.args and context.args[0].isdigit():
            target_id = int(context.args[0])
            member_obj = await context.bot.get_chat_member(chat.id, target_id)
            target = member_obj.user
        else:
            await message.reply_text("❌ يرجى الرد على رسالة المستخدم أو ذكر المعرف لإزالة التحذيرات.")
            return

    chat_warnings = warnings_counter.get(chat.id, {})
    if target.id in chat_warnings and chat_warnings[target.id] > 0:
        chat_warnings[target.id] = 0
        await message.reply_text(f"✅ تم إزالة جميع التحذيرات عن {target.first_name}.")
        logger.info(f"تم إزالة التحذيرات عن {target.id} بأمر من {user.id} في دردشة {chat.id}")
    else:
        await message.reply_text(f"ℹ️ لا توجد تحذيرات مسجّلة للمستخدم {target.first_name}.")
        logger.info(f"محاولة إزالة تحذيرات عن {target.id} ولكن لا توجد تحذيرات.")

async def pin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /pin
    يثبت الرسالة المردودة. للمشرفين فقط.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not await is_user_admin(update, user.id):
        await message.reply_text("📛 أنت لست مشرفًا في القروب تكرار الامر قد يعرضك للكتم.")
        return

    if not message.reply_to_message:
        await message.reply_text("❌ يرجى الرد على الرسالة التي تريد تثبيتها.")
        return

    target_msg = message.reply_to_message
    try:
        await context.bot.pin_chat_message(
            chat_id=chat.id,
            message_id=target_msg.message_id,
            disable_notification=False
        )
        await message.reply_text("📌 تم تثبيت الرسالة بنجاح.")
        logger.info(f"تم تثبيت الرسالة (ID: {target_msg.message_id}) في دردشة {chat.id}")
    except Exception as e:
        logger.error(f"خطأ أثناء تثبيت الرسالة: {e}")
        await message.reply_text("❌ حدث خطأ أثناء محاولة التثبيت.")

async def lock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /lock
    يقفل المجموعة مؤقتًا: لا يسمح للأعضاء بإرسال رسائل. مع إرسال صورة وأزرار.
    للمشرفين فقط.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not await is_user_admin(update, user.id):
        await message.reply_text("❌ أنت لست مشرفًا لتنفيذ هذا الأمر.")
        return

    try:
        # يمنع الأعضاء من إرسال الرسائل
        await context.bot.set_chat_permissions(
            chat_id=chat.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        # تحضير لوحة الأزرار
        keyboard = []
        for button_text, button_url in ALL_BUTTONS:
            keyboard.append([InlineKeyboardButton(button_text, url=button_url)])
        reply_markup = InlineKeyboardMarkup(keyboard)

        # إرسال الصورة مع الأزرار
        await context.bot.send_photo(
            chat_id=chat.id,
            photo=LOCK_IMAGE_URL,
            caption="الشات مقفل لعدم تواجد المشرفين⛔️.\nعند تواجد المشرفين راح يتم فتح القروب☑️.",
            reply_markup=reply_markup
        )
        logger.info(f"تم قفل المجموعة {chat.id} بأمر من {user.id}")
    except Exception as e:
        logger.error(f"خطأ أثناء قفل المجموعة: {e}")
        await message.reply_text("❌ حدث خطأ أثناء محاولة قفل المجموعة.")

async def unlock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /unlock
    يفتح المجموعة: يسمح للأعضاء بإرسال الرسائل ويرسل رسالة ترحيبية مع صورة.
    للمشرفين فقط.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    if not await is_user_admin(update, user.id):
        await message.reply_text("📛 أنت لست مشرفًا في القروب تكرار الامر قد يعرضك للكتم.")
        return

    try:
        # يسمح للأعضاء بإرسال الرسائل
        await context.bot.set_chat_permissions(
            chat_id=chat.id,
            permissions=ChatPermissions(can_send_messages=True)
        )
        # رسالة ترحيبية مع الصورة
        welcome_text = "🔓 تم فتح المجموعة، يسرنا عودتكم!\n✨ أهلاً وسهلاً بالجميع."
        await context.bot.send_photo(
            chat_id=chat.id,
            photo=LOCK_IMAGE_URL,
            caption=welcome_text
        )
        logger.info(f"تم فتح المجموعة {chat.id} بأمر من {user.id}")
    except Exception as e:
        logger.error(f"خطأ أثناء فتح المجموعة: {e}")
        await message.reply_text("❌ حدث خطأ أثناء محاولة فتح المجموعة.")

# =====================================
# معالج الأخطاء العام
# =====================================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء"""
    logger.error(f"خطأ في البوت: {context.error}", exc_info=True)
    if update and hasattr(update, "effective_message") and update.effective_message:
        try:
            await update.effective_message.reply_text("❌ حدث خطأ، يرجى المحاولة مرة أخرى.")
        except:
            pass

# =====================================
# الدالة الرئيسية لتشغيل البوت عبر Webhook
# =====================================
def main():
    if not BOT_TOKEN:
        logger.error("❌ التوكن غير محدد!")
        return
    if not WEBHOOK_URL:
        logger.error("❌ لم يتم تحديد EXTERNAL_URL!")
        return

    logger.info("🚀 بدء تشغيل البوت مع Webhook…")
    try:
        application = Application.builder().token(BOT_TOKEN).build()


        application.add_handler(currency_message_handler, group=0)
application.add_handler(give_handler)
application.add_handler(subtract_handler)
application.add_handler(balance_handler)


        # إضافة الـ Handlers الأساسية
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))

        # إضافة أوامر المشرفين
        application.add_handler(CommandHandler("ban", ban_command))
        application.add_handler(CommandHandler("unban", unban_command))
        application.add_handler(CommandHandler("kick", kick_command))
        application.add_handler(CommandHandler("mute", mute_command))
        application.add_handler(CommandHandler("unmute", unmute_command))
        application.add_handler(CommandHandler("warn", warn_command))
        application.add_handler(CommandHandler("clearwarn", clearwarn_command))
        application.add_handler(CommandHandler("pin", pin_command))
        application.add_handler(CommandHandler("lock", lock_command))
        application.add_handler(CommandHandler("unlock", unlock_command))

        # معالجة الرسائل النصية العامة (تنفيذ فقط عند المطابقة التامة للكلمة)
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)
        )

        # معالج الأخطاء
        application.add_error_handler(error_handler)

        # حذف أي تحديثات قديمة قبل تشغيل webhook
        application.bot.delete_webhook(drop_pending_updates=True)

        # تشغيل webhook: الاستماع على المنفذ الذي يوفره Render (ENV PORT)، ومسار URL هو التوكن
        port = int(os.getenv("PORT", "8443"))
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN,
            webhook_url=WEBHOOK_URL,
            drop_pending_updates=True
        )

    except Exception as e:
        logger.error(f"❌ فشل في تشغيل البوت: {e}", exc_info=True)

if __name__ == "__main__":
    main()
