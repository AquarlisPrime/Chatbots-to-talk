import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz
import random
from summa import summarizer

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram Bot Token (replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token)
TOKEN = '6594241798:AAFSLniwhFJttRoO2kIhZy5z3ziFkwOP8kw'

# Initialize the Telegram bot
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Command handler for /start command
def start(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm BrockBot. Ask me anything about Brock or Pokémon!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# Function to fetch information about Brock from online sources
def get_brock_info():
    try:
        # List of URLs to fetch information from
        urls = [
            f"https://en.wikipedia.org/wiki/Brock_(Pok%C3%A9mon)",
            f"https://pokemon.fandom.com/wiki/Brock_(anime)",
            f"https://www.pokemon.com/us",
            f"https://pokemon.fandom.com/wiki/Category:Main_characters"
        ]

        aggregated_text = ""

        for url in urls:
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find the main content section of the webpage
                main_content = soup.find('div', {'id': 'mw-content-text'})

                if main_content:
                    # Extract the text from the main content section
                    text = main_content.get_text()

                    # Perform text summarization using summa
                    summarized_text = summarizer.summarize(text, ratio=0.3)  # Adjust ratio for desired summary length
                    aggregated_text += summarized_text + "\n\n"

                    # Check if the aggregated text exceeds Telegram's message length limit
                    if len(aggregated_text) > 4096:
                        # Truncate the text to fit within the message length limit
                        aggregated_text = aggregated_text[:4096]
                        break  # Stop processing further URLs if the text is truncated

        if aggregated_text:
            return aggregated_text.strip()
        else:
            return "Sorry, I couldn't find information about Brock from the specified sources."

    except Exception as e:
        logging.error(f"Error fetching Brock info: {e}")
        return "Oops! Something went wrong while fetching information."


# Function to handle incoming messages
def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()

    # Define keywords to trigger specific actions
    if 'who is brock' in user_message:
        response = "Brock, known as Takeshi (タケシ) in Japan, is a fictional character in the Pokémon franchise owned by Nintendo. " \
                   "He is the Gym Leader of Pewter City and mainly uses Rock-type Pokémon. " \
                   "In the anime series, Ash first battles him and then accompanies him on his journey so that Brock can become a Pokémon breeder."
    elif any(pokemon_type in user_message for pokemon_type in ['rock', 'ground']):
        response = "Rock-type Pokémon are known for their sturdy defenses and powerful physical attacks. They are weak against Water, Grass, Ground, Steel, and Fighting-type moves."
    elif 'pokemon trainer' in user_message:
        response = "Brock is a Pokémon Trainer and the Gym Leader of Pewter City in the Pokémon games and anime series. " \
                   "He specializes in Rock-type Pokémon and is known for his role as one of Ash Ketchum's companions."
    elif 'pokemon' in user_message:
        response = "Brock is a character in the Pokémon franchise. He is the Gym Leader of Pewter City and is known for his Rock-type Pokémon."
    elif 'gym leader' in user_message:
        response = "Brock is a Gym Leader in the Pokémon games and anime. He specializes in Rock-type Pokémon and is the leader of Pewter City's gym."
    elif 'ash ketchum' in user_message:
        response = "Ash Ketchum is a Pokémon Trainer and the protagonist of the Pokémon anime series. He often travels with his friends, including Brock."
    else:
        response = "I'm sorry, I don't have information about that. Ask me anything about Brock, Pokémon types, or related topics!"

    context.bot.send_message(chat_id=update.effective_chat.id, text=response)

# Add message handler for text messages
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))


# Scheduler setup and task definition
scheduler = BackgroundScheduler()

def scheduled_task():
    # This function will be executed periodically based on the scheduler's configuration
    logging.info("Executing scheduled_task...")
    updater.bot.send_message(chat_id='YOUR_CHAT_ID', text="This is a scheduled message from BrockBot!")

# Add a scheduled job to execute 'scheduled_task' every 1 minute
scheduler.add_job(scheduled_task, IntervalTrigger(minutes=1, timezone=pytz.timezone('UTC')))  # Specify timezone using pytz

# Start the scheduler
scheduler.start()

# Start the Telegram bot
def main() -> None:
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
