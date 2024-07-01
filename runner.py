import google.generativeai as genai
import discord
import schedule
import json
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.members = True
client = discord.Client(intents=intents)
model = genai.GenerativeModel("gemini-1.5-flash")

config = {}
with open("config.json") as f:
    config = json.load(f)

genai.configure(api_key=config["keys"]["gemini"])


def get_gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return ""


async def send_discord_message(user_id, message):
    user = await client.fetch_user(user_id)
    if user is not None:
        try:
            await user.send(message)
        except Exception as e:
            print("Error sending message to user: ", user_id)
    else:
        print("User not found")


async def job():
    for friend in config["friends"]:
        user_id = friend["id"]
        print("User ID is: ", user_id)
        name = friend["name"]
        prompt = (
            config["prompt"]
            + " Their name is "
            + name
            + ". Please write in "
            + config["language"]
            + "."
        )
        print("Prompt is: ", prompt)
        response = get_gemini_response(prompt)
        if response == "":
            response = name + ", " + config["default_message"]
        print("Response is: ", response)
        await send_discord_message(user_id, response)


async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


@client.event
async def on_ready():
    await job()
    print(f"Logged in as {client.user}")
    schedule.every(config["minutes"]).minutes.do(asyncio.create_task, job())
    asyncio.create_task(scheduler())


client.run(config["keys"]["discord"])
