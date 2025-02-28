from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler, CallbackContext
from sqlalchemy import create_engine, MetaData, Table, create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import or_
from definition import Users, News_Base
import datetime
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
#Ideological sides
def similarity_cosine(points, values, extra_point):
    if points==[]:
        return 1
    # Reshape points and the extra point to 2D arrays for cosine similarity
    points = np.array(points)
    values=np.array(values)
    extra_point = np.array(extra_point).reshape(1, -1)  # Reshape to match dimensions

    # Compute the cosine similarities
    similarities = cosine_similarity(extra_point, points)

    # Normalize the similarity results to [0, 1]
    similarities_normalized = (similarities + 1) / 2  # Convert range from [-1, 1] to [0, 1]
    n=0
    for x, y in zip(similarities_normalized.flatten(), values):
        n+=x*y
    n/=np.sum(values)
    return n # Flatten to a 1D array of similarities

#Equality<->Markets
#Nation<->Globe
#Liberty<->Authority
#Tradition<->Progress
API_TOKEN = '6756208711:AAGEbHLyZaWUNEA_XqzNkB4nAheW2h3WrUs'
Engine = create_engine('postgresql://postgres:Pi2ruha_322@localhost/my_data_base')
Session = sessionmaker(bind=Engine)
session = Session()
countries = [f"Country {i}" for i in range(1, 101)]
Answers = ["Strongly agree", "Agree", "Neutral", "Disagree", "Strongly disagree"]
Reactions = ["0. Neutral.", "1. Like this.", "2. Strongly like this."]
Sides = {"Equality<->Markets": 0, "Nationalism<->Globalism": 0, "Liberalism<->Authoritarism": 0, "Traditionalism<->Progressivism": 0}
Ans_keys = [0,0,0,0,0,0,0,0,0,0,0,0]
Question_number = 0
#Direction based on agree
Questions = [
                ["The government should heavily regulate the market to reduce economic inequality.", "L"],
                ["Wealth redistribution through taxation is necessary to create a fair society.", "L"],
                ["Free markets alone can adequately address social and economic disparities.", "R"],
                ["National culture and identity should be prioritized over global integration.", "L"],
                ["Nations should always prioritize their interests, even if it harms global cooperation.", "L"],
                ["Global challenges like climate change should take precedence over national concerns.", "R"],
                ["Individuals should have the freedom to make their own choices, even if it conflicts with government rules.", "L"],
                ["Strong authority is necessary to maintain order, even at the expense of some personal freedoms.", "R"],
                ["Laws should limit personal liberties if it benefits the collective good.", "R"],
                ["Traditional values are essential and should guide decision-making in modern society.", "L"],
                ["Progress and innovation should take precedence over preserving traditional practices.", "R"],
                ["Society cannot advance without challenging and changing long-standing traditions.", "R"]
]
# /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_id = user.id
    first_name = user.first_name
    last_name = user.last_name
    username = user.username
    Item_To_Delete = session.query(Users).filter(Users.id == user_id).first()
    if Item_To_Delete:
        session.delete(Item_To_Delete)
        session.commit()
    User_Load = Users(id=user_id, 
                     First_Name=first_name, 
                     Last_Name=last_name, 
                     Username=username, 
                     Age=18, 
                     Language="ENG", 
                     Country="TR",
                     Readed_News={})
    session.add(User_Load)
    session.commit()
    await update.message.reply_text(f'Hello {first_name}! I am News reporter. Your data is saved.')

# /help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_id = user.id
    user_name = session.query(Users).filter(Users.id==user_id).first().Readed_News
    await update.message.reply_text(f'Help! {user_name.keys()}')

async def country_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_id = user.id
    if context.args[0]!="":
        user_is = session.query(Users).filter_by(id=user_id).first()
        user_is.country = context.args[0]
        session.commit()
        await update.message.reply_text(f"You are from {context.args[0]}")
    else:
        await update.message.reply_text(f"Field can not be empty. Use /country <country_name> to provide country")

async def age_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_id = user.id
    if context.args[0]!="":
        user_is = session.query(Users).filter_by(id=user_id).first()
        user_is.age = context.args[0]
        session.commit()
        await update.message.reply_text(f"Your age is {context.args[0]}")
    else:
        await update.message.reply_text(f"Field can not be empty. Use /age <age> to provide your age")
# /forcast Command (Fixed typo)
async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Here is your forecast!')


# /button Command to Send the Button
async def ideology_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global Question_number
    keyboard = [[InlineKeyboardButton(x, callback_data=x)] for x in Answers]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(Questions[Question_number][0], reply_markup=reply_markup)
    Question_number+=1
    #await update.message.reply_text("Wealth redistribution through taxation is necessary to create a fair society.", reply_markup=reply_markup)

def response(text: str) -> str:
    processed: str = text.lower()
    if "hello" in text:
        return "Hey there!"
    return "What"
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_type: str = update.message.chat.type
    text: str = update.message.text
    respon: str = response(text)
    print(respon)
    await update.message.reply_text(respon)
    #await update.message.reply_text("Wealth redistribution through taxation is necessary to create a fair society.", reply_markup=reply_markup)
async def News(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    Readed_News=session.query(Users).filter_by(id=user.id).first().Readed_News
    Potential=0
    Potential_Value=""
    for x in session.query(News_Base).all():
        if not str(x.id) in list(Readed_News.keys()):
            if  similarity_cosine([x[0] for x in Readed_News.values()], [x[1] for x in Readed_News.values()], x.Head_Line_Vector)>=Potential:
                Potential=similarity_cosine([x[0] for x in Readed_News.values()], [x[1] for x in Readed_News.values()], x.Head_Line_Vector)
                Potential_Value=x
            
    if Potential_Value!="":

        Readed_News[str(Potential_Value.id)]=[Potential_Value.Head_Line_Vector,1]
        session.query(Users).filter_by(id=user.id).first().Readed_News=dict(Readed_News)
        session.commit()
        keyboard = [[InlineKeyboardButton(x, callback_data=json.dumps([int(x[0]), user.id, str(Potential_Value.id)]))] for x in Reactions]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(text="<b>"+Potential_Value.Head_Line+"</b>\n\n"+''.join(["        "+sentence+"\n" for sentence in Potential_Value.Sentences])+''.join("#"+x+" " for x in Potential_Value.Topic)+f"\n#{Potential_Value.Country}\n{Potential_Value.Date_Time[0]}, {Potential_Value.Date_Time[1]}", reply_markup=reply_markup, parse_mode=ParseMode.HTML)
# Handle Button Press
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    button_data = json.loads(query.data)
    await query.answer()
    session.query(Users).filter_by(id=button_data[1]).first().Readed_News[button_data[2]][1]=button_data[0]
    session.commit()
    await query.edit_message_reply_markup(reply_markup=None)

# Main Function
def main() -> None:
    application = ApplicationBuilder().token(API_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("country", country_command))
    application.add_handler(CommandHandler("age", age_command))
    application.add_handler(CommandHandler("button", ideology_quiz))  # Added /button command
    application.add_handler(CommandHandler("news", News))
    # Echo Handler
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    #application.add_handler(MessageHandler(filters.ALL, reaction_handler))

    # Button Click Handler
    application.add_handler(CallbackQueryHandler(button_callback))


    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()



