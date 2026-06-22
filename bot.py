import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Ton TOKEN officiel
API_TOKEN = '8913363652:AAFNFZQM0fTbL4FBKbwFLk4bt5a64Sh9CZs'
bot = telebot.TeleBot(API_TOKEN)

# URL de ton serveur Flask
WEBAPP_URL = "https://victor-caused-measured-utilize.trycloudflare.com"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    prenom = message.from_user.first_name
    chat_id = message.chat.id
    user_id = message.from_user.id # Récupère le vrai ID Telegram de l'utilisateur
    
    texte_bienvenue = (
        f"🌟 **Bienvenue {prenom} sur Chahid Warbah 7 !** 🌟\n\n"
        "Cumule des points DZ en tapant sur ton écran et en remplissant "
        "nos missions quotidiennes de liens rémunérés.\n\n"
        "Clique sur le bouton ci-dessous pour lancer l'application 👇"
    )
    
    # On transmet l'ID dans l'URL pour Flask et le Javascript
    url_avec_id = f"{WEBAPP_URL}?user_id={user_id}"
    
    markup = InlineKeyboardMarkup()
    btn_ouvrir = InlineKeyboardButton(
        text="🚀 Lancer Chahid Warbah 7", 
        web_app=WebAppInfo(url=url_avec_id)
    )
    markup.add(btn_ouvrir)
    
    bot.send_message(chat_id, texte_bienvenue, parse_mode='Markdown', reply_markup=markup)

# FONCTION AJOUTÉE POUR LES NOTIFICATIONS
def send_notification(user_id, text):
    try:
        bot.send_message(user_id, text)
        return True
    except Exception as e:
        print(f"Erreur envoi notification : {e}")
        return False

if __name__ == '__main__':
    print("🤖 Bot Telegram Chahid Warbah 7 en cours d'exécution...")
    bot.infinity_polling()
