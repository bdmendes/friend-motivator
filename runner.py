import google.generativeai as genai
import discord
import json
import schedule
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
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


async def send_discord_message(user_id, text, message=None):
    user = await client.fetch_user(user_id)
    if user is not None:
        try:
            if message is not None:
                await message.reply(text)
            else:
                await user.send(text)
        except Exception as e:
            print("Error sending message to user: ", user_id)
    else:
        print("User not found")


async def job_friend(id, name, message=None):
    user_id = id
    print("User ID is: ", user_id)
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
    await send_discord_message(user_id, response, message=message)


async def job():
    for friend in config["friends"]:
        await job_friend(friend["id"], friend["name"])


async def timer():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    schedule.every(config["minutes"]).minutes.do(lambda: asyncio.ensure_future(job()))
    client.loop.create_task(timer())


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if "motiv" in message.content:
        await job_friend(message.author.id, message.author.name, message)


client.run(config["keys"]["discord"])
