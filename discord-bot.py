import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from discord import SelectOption
import requests

BOT_COMMAND_PREFIX = "!lc"
BASE_API_PATH = "http://127.0.0.1:5000/"
DSA_SHEET_ID_MAP = {
    "Neetcode150": 1
}


load_dotenv()

intents = discord.Intents.default()  
intents.message_content = True

bot = commands.Bot(command_prefix=BOT_COMMAND_PREFIX,intents=intents)

@bot.slash_command(name="ping", description="Responds with 'pong' to check bot functionality")
async def ping(ctx):
    await ctx.respond("pong!")

@bot.slash_command(name="help", description="user manual to bot")
async def help(ctx):
    await ctx.respond(
        """
        user manuel
        """
    )

def _check_if_user_exists(user_id):
    try:
        api_path = BASE_API_PATH + "users/check-existance/" + str(user_id)
        response = requests.get(api_path)
        if response.status_code == 200:
            data = response.json()
            return data.get("exists")
        else:
            raise Exception("Error in checking user existance through network call")
    except requests.RequestException as e:
        raise Exception(e)
    
def _create_user(user_id, user_name, email, webhook_string):
    data = {
        "user_id": user_id,
        "username": user_name,
        "email": email,
        "webhook_string": webhook_string,
        "is_deactive" : False,
        "work_starting_time": "9:00:00",
        "work_ending_time":"20:00:00",
        "active_plan_id": None
    }

    api_path = BASE_API_PATH + "users/create"

    try:
        response = requests.post(api_path, json=data)
        if response.status_code == 201:
            return True
        else:
            print(f"Failed to create user: {response.text}")
            return False
    
    except Exception as e:
        print(f"An error occurred: {e}")
        raise Exception(e)

async def _create_channel_and_get_webhook(guild, CATEGORY_NAME_FOR_NOTIFICATIONS, channel_name) :
    try:
        category = discord.utils.get(guild.categories, name=CATEGORY_NAME_FOR_NOTIFICATIONS)
        
        if not category:
            category = await guild.create_category(CATEGORY_NAME_FOR_NOTIFICATIONS)

        channel = await guild.create_text_channel(channel_name, category=category)
        webhook = await channel.create_webhook(name=f"user_channel")

        return webhook
    
    except discord.errors.HTTPException as e:
        raise Exception(f'Error creating channel: {e}')
    except Exception as e:
        raise Exception(f'An error occurred: {e}')

def _create_plan(user_id, dsa_sheet_id, problem_frequency):
    api_path = BASE_API_PATH + "plans/initiate"
    data = {"user_id": user_id, "dsa_sheet_id": dsa_sheet_id, "problem_frequency": problem_frequency}
    try:
        response = requests.post(api_path, json=data)
        if response.status_code == 201:
            return response.content["plan_id"]
        else:
            raise Exception(f"Failed to initiate plan: {response.text}")
    
    except Exception as e:
        raise Exception(e)

def _activate_plan(user_id, plan_id):
    api_path = BASE_API_PATH + "users/set-active-plan"
    data = {"user_id": user_id, "active_plan_id": plan_id}
    try:
        response = requests.post(api_path, json=data)
        if response.status_code == 201:
            return response.content
        else:
            print(f"Failed to activate plan: {response.text}")
            raise Exception("Error in setting active plan: ", response.content)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        raise Exception(e)

async def _fetch_user_plan_ids(user_id):
    pass

async def _get_plan_details(plan_id):
    pass

async def _get_user_active_plan_id(user_id):
    pass

@bot.slash_command(name="create-user", description="creates user account with default parameters")
async def create_account(ctx):
    try:
        is_user_exists = _check_if_user_exists(str(ctx.author.id))
        if is_user_exists:
            await ctx.respond("User account already exists")
            return

        guild = discord.utils.get(bot.guilds)
        webhook = await _create_channel_and_get_webhook(guild, os.getenv("CATEGORY_NAME_FOR_NOTIFICATIONS"), ctx.author.name)
        is_successful = _create_user(ctx.author.id, ctx.author.name, "dummy@email.com", webhook.url)

        if is_successful:
            await ctx.respond("User account has been created. Default configuration is set. To make changes, learn more.")
        else:
            await ctx.respond("Failed to create user account. Please try again later.")
    except Exception as e:
        await ctx.respond(f"An error occurred: {str(e)}")

class Dropdown(discord.ui.Select):
    def __init__(self, placeholder, labels, func_callback, descriptions=None):
        options = [discord.SelectOption(label=label) for label in labels]
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)

        self.func_callback = func_callback  

    async def callback(self, interaction: discord.Interaction):
        try:
            await self.func_callback(interaction)
        except Exception as e:
            print(f"Error in dropdown callback: {e}")
            await interaction.response.send_message(f"An unexpected error occurred. Please try again later.")
            raise Exception("Error in dropdown. {e}")
    
    def get_result(self):
        return self.values[0]
    
class DropdownView(discord.ui.View):
    def __init__(self, placeholder, labels, func_callback):
        super().__init__()
        self.dropdown = Dropdown(placeholder, labels, func_callback)
        self.add_item(self.dropdown)
    
    def get_result(self):
        return self.dropdown.get_result()


@bot.slash_command(name="create-new-plan", description="creates a new dsa plan")
async def create_new_plan(ctx):

    async def handle_dsa_sheet_selection(interaction):
        try:
            selected_option = interaction.data["values"][0]
            if selected_option == "Cancel":
                return None
            dsa_sheet_id = DSA_SHEET_ID_MAP[selected_option]
            return dsa_sheet_id
        except Exception as e:
            print(f"Error in handling DSA sheet selection: {e}")
            return None

    async def handle_problem_freq_selection(interaction):
        try:
            selected_option = interaction.data["values"][0]
            return selected_option
        except Exception as e:
            print(f"Error in handling problem frequency selection: {e}")
            return None

    async def handle_activation_selection(interaction):
        try:
            selected_option = interaction.data["values"][0]
            return selected_option
        except Exception as e:
            print(f"Error in handling activation selection: {e}")
            return None

    try:
        # DSA Sheet Selection
        dsa_sheet_options = ["Neetcode150", "...", "Cancel"]
        dsa_sheet_view = await bot.wait_for(DropdownView(placeholder="Choose DSA sheet", labels=dsa_sheet_options, func_callback=handle_dsa_sheet_selection))
        await ctx.send('Creating new plan...', view=dsa_sheet_view)
        dsa_sheet_id = await dsa_sheet_view.get_result()

        if not dsa_sheet_id:
            await ctx.respond("Plan creation cancelled")
            return
        
        problem_freq_options = [1, 2, 3, 4, 5, 6, 7]
        problem_freq_view = await bot.wait_for(DropdownView(placeholder="Daily problem frequency", labels=problem_freq_options, func_callback=handle_problem_freq_selection))
        await ctx.send('Choose how many problems you are willing to solve in a day', view=problem_freq_view)
        problem_frequency = await problem_freq_view.get_result()

        if problem_frequency is None:
            await ctx.respond("Plan creation cancelled.")
            return

        plan_id = _create_plan(ctx.author.id, dsa_sheet_id, problem_frequency)

        # Activation Selection
        activation_choices = ["Yes", "No"]
        activation_view = DropdownView(placeholder="Do you want to activate this plan?", labels=activation_choices, func_callback=handle_activation_selection)
        await ctx.send('Do you want to activate this plan?', view=activation_view)
        activation_choice = await activation_view.get_result()

        if activation_choice is None:
            await ctx.respond("Plan creation cancelled.")
            return

        if activation_choice == "No":
            await ctx.respond("Plan has been created but not set active. Head to config > Plans to activate.")
            return

        _activate_plan(ctx.author.id, plan_id)
        await ctx.respond("Plan has been created and set active.")

    except Exception as e:
        await ctx.respond(f"An error occurred in creating plan: {str(e)}")


async def _handle_plans_config(ctx):
    plans_config_options = ["view all plans", "set active plan", "update daily problem frequency", "Cancel"]
    plans_config_setting = await ctx.interaction.response.send_message(
        "Choose Plans Config setting",
        components=[discord.SelectMenu(options=[SelectOption(label=option) for option in plans_config_options])]
    )
    plans_config_choice = int(plans_config_setting.data["values"][0])
    if plans_config_options[plans_config_choice] == "Cancel":
        return
    
    if plans_config_options[plans_config_choice] == "view all plans":
        plan_ids = await _fetch_user_plan_ids(ctx.author.id)  
        if plan_ids is None or len(plan_ids) == 0:
            await ctx.respond("You don't have any plans yet.")
            return
        plan_message = "**Your Plans:**\n"
        for plan_id in plan_ids:
            plan_details = await _get_plan_details(plan_id) 
            plan_message += f"- Plan ID: {plan_id}\n  Details: {plan_details}\n"
        await ctx.respond(plan_message)

    elif plans_config_options[plans_config_choice] == "set active plan":
        plan_ids = await _fetch_user_plan_ids(ctx.author.id)  
        if plan_ids is None or len(plan_ids) == 0:
            await ctx.respond("You don't have any plans yet.")
            return
        plan_details = [_get_plan_details(plan_id) for plan_id in plan_ids]

        plan_options = [SelectOption(label=f"Plan ID: {plan_id} --  {plan_detail}") for plan_id, plan_detail in zip(plan_ids, plan_details)]

        plan_choice = await ctx.interaction.response.edit_message(
            content="Choose the plan you want to activate:",
            components=[discord.SelectMenu(options=plan_options)]
        )
        chosen_plan_id = plan_ids[int(plan_choice.data["values"][0])]

        try:
            _activate_plan(ctx.author.id, chosen_plan_id) 
            await ctx.respond(f"Plan with ID: {chosen_plan_id} is now your active plan.")

        except Exception as e:
            print(f"Error setting active plan: {e}")
            await ctx.respond(f"An error occurred. Please try again later.")


    elif plans_config_options[plans_config_choice] == "update daily problem frequency":
        active_plan_id = await _get_user_active_plan_id(ctx.author.id)  
        if active_plan_id is None:
            await ctx.respond("You don't have any active plans yet.")
            return
        plan_details = await _get_plan_details(active_plan_id)
        await ctx.respond(f"Active plan details {plan_details}")


        confirmation_message = f"You are about to update the daily problem frequency for your active plan (ID: {active_plan_id}). Are you sure you want to continue?"
        confirmation_choices = ["Yes", "No"]
        confirmation_choice = await ctx.interaction.response.edit_message(
            content=confirmation_message,
            components=[discord.SelectMenu(options=[SelectOption(label=option) for option in confirmation_choices])]
        )

        if confirmation_choice.data["values"][0] == "No":
            return  # User cancels update

        problem_frequency_options = [1, 2, 3, 4, 5, 6]
        problem_frequency_choice = await ctx.interaction.response.edit_message(
            content="How many problems are you willing to solve in a day?",
            components=[discord.SelectMenu(options=[SelectOption(label=str(option)) for option in problem_frequency_options])]
        )
        new_problem_frequency = int(problem_frequency_choice.data["values"][0])

        data = {"user_id": ctx.author.id, "new_frequency": new_problem_frequency}
        try:
            response = requests.post(url=BASE_API_PATH + "plans/update-frequency", data=data)
            if response.status_code == 200:
                await ctx.respond(f"Daily problem frequency for your active plan has been updated to: {new_problem_frequency}.")
            else:
                await ctx.respond(f"Failed to update frequency. Error: {response.text}")
        except Exception as e:
            print(f"An error occurred during frequency update: {e}")
            await ctx.respond(f"An error occurred. Please try again later.")


async def _handle_notification_params_config(ctx):
    pass

async def _handle_user_config(ctx):
    pass


@bot.slash_command(name="config", description="configure your plans, notification params, etc")
async def config(ctx):
    try:
        config_options = ["Plans", "Notification Params", "User Config", "Cancel"]  
        config_setting = await ctx.interaction.response.send_message(
            "Choose Config setting",
            components=[discord.SelectMenu(options=[SelectOption(label=option) for option in config_options])]
        )
        config_choice = int(config_setting.data["values"][0])
        if config_options[config_choice] == "Cancel":
            return
        
        if config_options[config_choice] == "Plans":
            await _handle_plans_config(ctx)

        elif config_options[config_choice] == "User Config":
            await _handle_user_config(ctx)

        elif config_options[config_choice] == "Notification Params":
            await _handle_notification_params_config(ctx)

        
    except Exception as e:
        await ctx.respond(f"An error occurred in setting up config. {str(e)}")


bot.run(os.getenv("BOT_TOKEN"))

