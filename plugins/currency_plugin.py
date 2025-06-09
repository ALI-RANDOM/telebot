
import json
import os
import asyncio
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes

# === ملف تخزين العملات والعدادات ===
DATA_FILE = "currency_data.json"

# إنشاء بنية البيانات الأولية إن لم تكن موجودة
if not os.path.isfile(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"balances": {}, "msg_counts": {}}, f, ensure_ascii=False)

# دوال للوصول للبيانات
async def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

async def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

# === معالج الرسائل لحساب النقاط ===
async def count_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = await load_data()
    data["msg_counts"][user_id] = data["msg_counts"].get(user_id, 0) + 1
    # كل 500 رسالة يمنح عملة
    if data["msg_counts"][user_id] >= 500:
        data["msg_counts"][user_id] = 0
        data["balances"][user_id] = data["balances"].get(user_id, 0) + 1
        await update.message.reply_text(
            f"🎉 مبروك {update.effective_user.first_name}! ربحت عملة واحدة. رصيدك الآن: {data['balances'][user_id]} عملات."
        )
    await save_data(data)

# === أوامر المشرفين لإعطاء/خصم العملات ===
async def give_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        return await update.message.reply_text("❌ استخدم: /give <user_id> <amount>")
    target_id, amount = context.args[0], context.args[1]
    if not amount.isdigit():
        return await update.message.reply_text("❌ المبلغ يجب أن يكون رقمًا.")
    amt = int(amount)
    data = await load_data()
    bal = data["balances"].get(target_id, 0) + amt
    data["balances"][target_id] = bal
    await save_data(data)
    await update.message.reply_text(f"✅ أضفت {amt} عملات للمستخدم {target_id}. الرصيد الآن: {bal}.")

async def deduct_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        return await update.message.reply_text("❌ استخدم: /deduct <user_id> <amount>")
    target_id, amount = context.args[0], context.args[1]
    if not amount.isdigit():
        return await update.message.reply_text("❌ المبلغ يجب أن يكون رقمًا.")
    amt = int(amount)
    data = await load_data()
    bal = max(data["balances"].get(target_id, 0) - amt, 0)
    data["balances"][target_id] = bal
    await save_data(data)
    await update.message.reply_text(f"✅ خصمت {amt} عملات من المستخدم {target_id}. الرصيد الآن: {bal}.")

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = await load_data()
    bal = data["balances"].get(user_id, 0)
    await update.message.reply_text(f"💰 رصيدك الحالي: {bal} عملات.")

# === تسجيل handlers ===
def register(application):
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, count_messages), group=1)
    application.add_handler(CommandHandler("give", give_command), group=2)
    application.add_handler(CommandHandler("deduct", deduct_command), group=2)
    application.add_handler(CommandHandler("balance", balance_command), group=1)
