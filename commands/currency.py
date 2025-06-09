import os
import json
import asyncio
from telegram import Update
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

# -------------------------------------
# إعداد مسار ملف البيانات
# -------------------------------------
DATA_FILE = "currency_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -------------------------------------
# دالة للتحقق من صلاحيات المشرف
# -------------------------------------
async def is_admin(update: Update, user_id: int) -> bool:
    try:
        member = await update.effective_chat.get_member(user_id)
        return member.status in ("administrator", "creator")
    except:
        return False

# -------------------------------------
# معالج الرسائل لحساب واحتساب العملات
# -------------------------------------
async def currency_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or msg.from_user.is_bot:
        return

    user_id = str(msg.from_user.id)
    data = load_data()
    user = data.get(user_id, {"messages": 0, "currency": 0, "next_award": 500})

    user["messages"] += 1
    # عند بلوغ العتبة، نضيف 1 عملة ونرفع العتبة بمقدار 500 رسالة
    if user["messages"] >= user["next_award"]:
        user["currency"] += 1
        user["next_award"] += 500
        await msg.reply_text(
            f"🎉 مبروك! حصلت على 1 عملة لبلوغهك {user['next_award']-500} رسالة.\n"
            f"رصيدك الآن: {user['currency']} عملة."
        )

    data[user_id] = user
    save_data(data)

currency_message_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    currency_message
)

# -------------------------------------
# أمر إعطاء العملات (/اعطي) – رد على رسالة المستخدم مع عدد النقاط
# -------------------------------------
async def give_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user

    if not await is_admin(update, user.id):
        return await msg.reply_text("🚫 فقط المشرفون يمكنهم استخدام هذا الأمر.")

    if not msg.reply_to_message or not context.args:
        return await msg.reply_text("❌ استخدم الأمر بالرد على رسالة المستخدم: `/اعطي <عدد>`")

    try:
        amount = int(context.args[0])
    except:
        return await msg.reply_text("❌ الرجاء إدخال عدد صحيح.")

    target = msg.reply_to_message.from_user
    data = load_data()
    target_id = str(target.id)
    user_data = data.get(target_id, {"messages": 0, "currency": 0, "next_award": 500})
    user_data["currency"] += amount
    data[target_id] = user_data
    save_data(data)

    await msg.reply_text(
        f"✅ تم إضافة {amount} عملة إلى {target.mention_html()}.\n"
        f"رصيده الآن: {user_data['currency']} عملة.",
        parse_mode="HTML"
    )

# -------------------------------------
# أمر خصم العملات (/خصم) – رد على رسالة المستخدم مع عدد النقاط
# -------------------------------------
async def subtract_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user

    if not await is_admin(update, user.id):
        return await msg.reply_text("🚫 فقط المشرفون يمكنهم استخدام هذا الأمر.")

    if not msg.reply_to_message or not context.args:
        return await msg.reply_text("❌ استخدم الأمر بالرد على رسالة المستخدم: `/خصم <عدد>`")

    try:
        amount = int(context.args[0])
    except:
        return await msg.reply_text("❌ الرجاء إدخال عدد صحيح.")

    target = msg.reply_to_message.from_user
    data = load_data()
    target_id = str(target.id)
    user_data = data.get(target_id, {"messages": 0, "currency": 0, "next_award": 500})
    user_data["currency"] = max(0, user_data["currency"] - amount)
    data[target_id] = user_data
    save_data(data)

    await msg.reply_text(
        f"✅ تم خصم {amount} عملة من {target.mention_html()}.\n"
        f"رصيده الآن: {user_data['currency']} عملة.",
        parse_mode="HTML"
    )

# -------------------------------------
# أمر عرض الرصيد (/رصيدي)
# -------------------------------------
async def my_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    bal = data.get(user_id, {}).get("currency", 0)
    await update.effective_message.reply_text(f"💰 رصيدك: {bal} عملة.")

give_handler      = CommandHandler("اعطي", give_currency)
subtract_handler  = CommandHandler("خصم", subtract_currency)
balance_handler   = CommandHandler("رصيدي", my_balance)
