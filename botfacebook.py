# استيراد المكتبات المطلوبة
import telegram
import requests
import io

# إنشاء كائن البوت باستخدام رمز API الخاص بك
bot = telegram.Bot(token="6502455740:AAGjMhh_fCNQUCvsNpKqHRgyirjiDr3cbEk")

# تعريف دالة للتحقق من صحة رابط الفيسبوك
def is_valid_facebook_url(url):
    # إذا كان الرابط يبدأ بـ https://www.facebook.com/ ويحتوي على /videos/ ، فإنه رابط صالح
    if url.startswith("https://www.facebook.com/") and "/videos/" in url:
        return True
    else:
        return False

# تعريف دالة للحصول على رابط التحميل من رابط الفيسبوك
def get_download_url(url):
    # إرسال طلب GET إلى رابط الفيسبوك
    response = requests.get(url)
    # إذا كان الطلب ناجحًا
    if response.status_code == 200:
        # استخراج نص HTML من الاستجابة
        html = response.text
        # البحث عن علامة <video> في HTML
        video_tag = html.split("<video")[1]
        # البحث عن خاصية src في علامة <video>
        src_attr = video_tag.split("src=")[1]
        # استخراج قيمة خاصية src ، والتي هي رابط التحميل
        download_url = src_attr.split('"')[1]
        # إرجاع رابط التحميل
        return download_url
    else:
        # إذا كان الطلب فاشلاً ، إرجاع None
        return None

# تعريف دالة للتعامل مع رسائل المستخدمين
def handle_messages(update, context):
    # الحصول على نص الرسالة من المستخدم
    message_text = update.message.text
    # الحصول على معرف المحادثة من المستخدم
    chat_id = update.message.chat_id
    # إذا كان نص الرسالة رابطًا للفيسبوك
    if is_valid_facebook_url(message_text):
        # إرسال رسالة للمستخدم تخبره بأننا نعمل على تحميل الفيديو
        bot.send_message(chat_id=chat_id, text="جارٍ تحميل فيديو من الفيسبوك ...")
        # الحصول على رابط التحميل من رابط الفيسبوك
        download_url = get_download_url(message_text)
        # إذا تم العثور على رابط التحميل
        if download_url is not None:
            # إرسال طلب GET إلى رابط التحميل
            response = requests.get(download_url)
            # إذا كان الطلب ناجحًا
            if response.status_code == 200:
                # إنشاء كائن io.BytesIO من المحتوى الثنائي للاستجابة
                video_file = io.BytesIO(response.content)
                # إرسال الفيديو للمستخدم
                bot.send_video(chat_id=chat_id, video=video_file)
            else:
                # إذا كان الطلب فاشلاً ، إرسال رسالة خطأ للمستخدم
                bot.send_message(chat_id=chat_id, text="عذرًا ، حدث خطأ أثناء تحميل الفيديو.")
        else:
            # إذا لم يتم العثور على رابط التحميل ، إرسال رسالة خطأ للمستخدم
            bot.send_message(chat_id=chat_id, text="عذرًا ، لم نتمكن من العثور على رابط التحميل لهذا الفيديو.")
    else:
        # إذا كان نص الرسالة ليس رابطًا للفيسبوك ، إرسال رسالة تعليمية للمستخدم
        bot.send_message(chat_id=chat_id, text="هذا البوت يمكنه تحميل فيديوهات من الفيسبوك فقط. يرجى إرسال رابط صالح لفيديو من الفيسبوك.")

# إنشاء كائن معالج التحديثات
updater = telegram.ext.Updater(bot=bot, use_context=True)

# إضافة معالج للرسائل النصية
updater.dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, handle_messages))

# بدء استقبال التحديثات من تيليجرام
updater.start_polling()

# تشغيل البوت حتى يتم الضغط على Ctrl + C
updater.idle()
