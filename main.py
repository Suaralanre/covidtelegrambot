#!/usr/bin/env python 3

import os, asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from countries import country_list
from api_generator import summary



# getting token from os profile
token = os.environ.get("COVID_API_TOKEN",) 
# create bot object
bot = Bot(token=token)
# create a Dispatcher for this instance
dp = Dispatcher(bot=bot)

#  \N{SOS button}
help_button = InlineKeyboardButton("How to Use Me \U0001F198"
                                   ,callback_data="cb_help")
keyb = InlineKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True).add(help_button)


async def main():
    # I needed this wrapper function because it gives me better control.
    # You might not need it at all


    @dp.message_handler(commands=["start"])
    async def send_welcome(message: types.Message) -> None:
        # message reply for starting the bot
        await message.reply("Hi \U0001F44B \n\nI will give you info and updates about COVID-19"
                            " in any country of your choice."
                            "\n\n Use the button below to learn"
                            " how to use me",
                            reply_markup=keyb)


    async def help_message(message: types.Message) -> None:
        return message == "Help"

    @dp.callback_query_handler(text=["cb_help"])
    async def search_info(call: types.CallbackQuery) -> None:
        # return message for using the help button
        if call.data == "cb_help":
            await call.message.answer("For a single name country, e.g. type: 'Nigeria'\n\n"
                                "For a compound name country separate each word by hyphen(-)\n"
                                  "e.g.'United-kingdom'\n\n"
                                  "All letters can be in either upper-case or lower-case or both\n\n"
                                  "Have fun \U0001F60B"
                                )

    async def country_setup():
        # getting all the available countries in a list
        my_country = []
        country = country_list()
        for i in range(len(country)):
            my_country.append(country[i]["Slug"])
        return my_country
    
   # Ensure that countries data is fully loaded before proceeding
    countries = await country_setup()
    
    async def check_country(message, country):# Flag to assert that given message matches given country
        match =  message==country
        return match

    async def country_filter(message: types.Message): 
        # filter that will be passed to custom filters
    
    	# sets up task to check for match for each country in the list simultaneously
        futures = [asyncio.ensure_future(check_country(message.text.lower(), country)) for country in countries]
         
        results = await asyncio.gather(*futures)# collects results of the tasks when they are completed. Each Task will produce a true or false value
        return any(results)# returns true if at least one of the results is True, i.e there is at least one country that matches user input


    @dp.message_handler(country_filter)
    # Apparently, the custom_filters argument doesn't just any coroutine, 
    # it wants one that can take the user message, 
    # process it and then return a boolean to determine whether the message should be processed or not.
    # This is exactly what country_filter() does
    async def return_api_message(message: types.Message) -> None:
        
        info_country = await summary() #You forgot to await summary() here. It's a coroutine
        my_input = str(message.text).lower()


        for i in range(len(info_country["Countries"])): 
            # You iterated over len(len(info_country["Countries"])) 
            # instead of range(len(info_country["Countries"])). 
            # The former is not iterable.
            
            if info_country["Countries"][i]["Slug"] == my_input:
                user_country = info_country["Countries"][i]["Country"]
                new_confirmed = info_country["Countries"][i]["NewConfirmed"]
                total_confirmed = info_country["Countries"][i]["TotalConfirmed"]
                new_deaths = info_country["Countries"][i]["NewDeaths"]
                total_deaths = info_country["Countries"][i]["TotalDeaths"]
                new_recovered = info_country["Countries"][i]["NewRecovered"]
                total_recovered = info_country["Countries"][i]["TotalRecovered"]
                date = info_country["Countries"][i]["Date"]
        
        await message.answer("\U0001F44D Please gimme a few seconds.",)
        await asyncio.sleep(1)
        await message.answer(f"Country: {user_country}\n"
                        f"Date: {date}\n"
                        f"Newly Confirmed Cases: {new_confirmed}\n"
                        f"Total Confirmed Cases: {total_confirmed}\n"
                        f"New Deaths: {new_deaths}\n"
                        f"Total Deaths: {total_deaths}\n"
                        f"Newly Recovered Cases: {new_recovered}\n"
                        f"Total Recovered Cases: {total_recovered}\n")
            
    @dp.message_handler()
    async def invalid_country(message: types.Message) -> str:
        await message.answer("Sorry, \U0001F615 \n\nI don't know this country", 
                             reply_markup=keyb)

    await dp.start_polling()




if __name__ == "__main__":
    asyncio.run(main())
    


    

 
