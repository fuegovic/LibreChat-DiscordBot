import os
import subprocess
import time
import asyncio
import discord
from discord.ext import commands
import bot_config
from getpass import getpass

# Set the bot's token, user ID and working directory in "bot_config.py"
TOKEN = bot_config.TOKEN
USER_ID = bot_config.USER_ID
WORKING_DIR = bot_config.WORKING_DIR

# Check if the operating system is Unix-like, not Windows
if os.name == 'posix':
    SUDO_PASSWORD = getpass("Enter your sudo password: ")
else:
    SUDO_PASSWORD = None

# Create an instance of the bot with the provided token and user ID
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents, heartbeat_timeout=60)

# Define a check function to verify if the user executing a command is the specified user
@bot.check
def is_user(ctx):
    return str(ctx.author.id) == USER_ID

# Define an event function that runs when the bot is ready and prints a message indicating the bot's connection
@bot.event
async def on_ready():
    print(f'Connected as {bot.user.name}')
    await bot.tree.sync ()

# Docker "Status" command
@bot.hybrid_command(name="status", description="Docker status")
async def status(ctx):
    os.chdir(WORKING_DIR) # Change the working directory to the specified folder
    #status_message = await ctx.send('Getting Docker status...')
    command = 'docker ps -a'
    await execute_command_with_status_message(ctx, command)

# LibreChat docker-compose.yml:
# Docker "Start" command
@bot.hybrid_command(name="start", description="Start Docker")
async def start(ctx):
    os.chdir(WORKING_DIR) # Change the working directory to the specified folder
    status_message = await ctx.send('Starting docker...')
    command = 'docker-compose up -d'
    await execute_command_with_status_message(ctx, command)

# Docker "Stop" command
@bot.hybrid_command(name="stop", description="Stop Docker")
async def stop(ctx):
    os.chdir(WORKING_DIR) # Change the working directory to the specified folder
    status_message = await ctx.send('Stopping docker...')
    command = 'docker-compose stop'
    await execute_command_with_status_message(ctx, command)

# Docker "Update" command   
@bot.hybrid_command(name="update", description="Update LibreChat")
async def update(ctx):
    os.chdir(WORKING_DIR) # Change the working directory to the specified folder
    status_message = await ctx.send('Update in progress...')
    start_time = time.time()
    commands = [
        'npm run update:docker',
        'docker-compose up -d'
    ]
    await execute_commands_with_status_messages(ctx, commands)
    elapsed_time = time.time() - start_time
    await status_message.edit(content=f'Update completed in {elapsed_time:.2f} seconds.')

# LibreChat sudo docker-compose.yml:
# Docker "Start-sudo" command
@bot.hybrid_command(name="start-sudo", description="Start Docker with sudo")
async def start_sudo(ctx):
    os.chdir(WORKING_DIR) # Change the working directory to the specified folder
    status_message = await ctx.send('Starting docker...')
    command = 'sudo docker-compose up -d'
    await execute_command_with_status_message(ctx, command)

# Docker "Stop-sudo" command
@bot.hybrid_command(name="stop-sudo", description="Stop Docker with sudo")
async def stop_sudo(ctx):
    os.chdir(WORKING_DIR) # Change the working directory to the specified folder
    status_message = await ctx.send('Stopping docker...')
    command = 'sudo docker-compose stop'
    await execute_command_with_status_message(ctx, command)

# Docker "Update" command   
@bot.hybrid_command(name="update-sudo", description="Update LibreChat")
async def update(ctx):
    os.chdir(WORKING_DIR) # Change the working directory to the specified folder
    status_message = await ctx.send('Update in progress...')
    start_time = time.time()
    commands = [
        'sudo npm run update:docker',
        'sudo docker-compose up -d'
    ]
    await execute_commands_with_status_messages(ctx, commands)
    elapsed_time = time.time() - start_time
    await status_message.edit(content=f'Update completed in {elapsed_time:.2f} seconds.')


# LibreChat single-compose.yml:
# Docker "start-single" command
@bot.hybrid_command(name="start-single", description="Start Docker with single-compose.yml")
async def start_single(ctx):
    os.chdir(WORKING_DIR) # Change the working directory to the specified folder
    status_message = await ctx.send('Starting docker...')
    command = 'docker-compose -f ./docs/dev/single-compose.yml up -d'
    await execute_command_with_status_message(ctx, command)

# Docker "stop-single" command
@bot.hybrid_command(name="stop-single", description="Stop Docker with single-compose.yml")
async def stop_single(ctx):
    os.chdir(WORKING_DIR) # Change the working directory to the specified folder
    status_message = await ctx.send('Stopping docker...')
    command = 'docker-compose -f ./docs/dev/single-compose.yml stop'
    await execute_command_with_status_message(ctx, command)

# Docker "update-s" command   
@bot.hybrid_command(name="update-single", description="Update LibreChat - single-compose.yml")
async def update_single(ctx):
    os.chdir(WORKING_DIR) # Change the working directory to the specified folder
    status_message = await ctx.send('Update in progress...')
    start_time = time.time()
    commands = [
        'npm run update:single',
        'docker-compose -f ./docs/dev/single-compose.yml up -d'
    ]
    await execute_commands_with_status_messages(ctx, commands)
    elapsed_time = time.time() - start_time
    await status_message.edit(content=f'Update completed in {elapsed_time:.2f} seconds.')

# LibreChat local
# Local "start-local" command
@bot.hybrid_command(name="start-local", description="Start local")
async def start_local(ctx):
    os.chdir(WORKING_DIR) # Change the working directory to the specified folder
    status_message = await ctx.send('Starting LibreChat...')
    command = 'npm run backend'
    await execute_command_with_status_message(ctx, command)

# Local "stop-local" command
@bot.hybrid_command(name="stop-local", description="Stop local")
async def stop_local(ctx):
    os.chdir(WORKING_DIR) # Change the working directory to the specified folder
    status_message = await ctx.send('Stopping LibreChat...')
    command = 'npm run backend:stop'
    await execute_command_with_status_message(ctx, command)

# Local "Update" command   
@bot.hybrid_command(name="update-local", description="Update local")
async def update_local(ctx):
    os.chdir(WORKING_DIR) # Change the working directory to the specified folder
    status_message = await ctx.send('Update in progress...')
    start_time = time.time()
    commands = [
        'npm run backend:stop'
        'npm run update:local',
        'npm run backend'
    ]
    await execute_commands_with_status_messages(ctx, commands)
    elapsed_time = time.time() - start_time
    await status_message.edit(content=f'Update completed in {elapsed_time:.2f} seconds.')

# Config working directory
@bot.command(name="config", description="Change working directory")
async def config(ctx):
    global WORKING_DIR
    current_working_dir = WORKING_DIR

    # This will make sure that the response will only be registered if the following
    # conditions are met:
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    await ctx.send("Enter the new working directory")

    try:
        # Wait for a message that satisfies the check
        msg = await bot.wait_for("message", check=check, timeout=30) # 30 seconds to reply
        new_working_dir = msg.content # Get the content of the message
    except asyncio.TimeoutError:
        # If the user doesn't reply within 30 seconds, send a message
        await ctx.send("Sorry, you didn't reply in time!")
        return # End the command here

    if new_working_dir == current_working_dir:
        await ctx.send(f"The current working directory is already set to: {current_working_dir}")
    else:
        WORKING_DIR = new_working_dir

        # Update the working directory in bot_config.py
        with open("bot_config.py", "r") as config_file:
            lines = config_file.readlines()

        for i in range(len(lines)):
            if lines[i].startswith("WORKING_DIR"):
                lines[i] = f'WORKING_DIR = "{new_working_dir}"\n'
                break

        with open("bot_config.py", "w") as config_file:
            config_file.writelines(lines)

        await ctx.send(f"Working directory changed from {current_working_dir} to: {new_working_dir}")


# Remove the default help command
bot.remove_command('help')

@bot.command(name='help', description="Returns all commands available")
async def help(ctx):
    help_embed = discord.Embed(title="Help", description="List of Commands:", color=0x00ff00)
    for command in bot.commands:
        #only include the commands that the user can run
        if not command.hidden and command.enabled and len(set(command.checks).intersection(set(bot.checks)))==len(command.checks):
            help_embed.add_field(name=f"/{command.name}", value=command.description, inline=False)
    await ctx.send(embed=help_embed)

# Function to execute a command and display the status message and log output
async def execute_command_with_status_message(ctx, command):
    start_time = time.time()
    status = await ctx.send(f'Command "{command}"')

    if command.startswith("sudo") and SUDO_PASSWORD is not None:
        # Create a Popen instance with a pipe to stdin
        process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # Write the sudo password to stdin
        process.stdin.write(SUDO_PASSWORD + "\n")
    else:
        process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = await process.communicate()
    elapsed_time = time.time() - start_time

    output = stdout.decode() if stdout else stderr.decode()
    log_message = output[-750:]  # Last 750 characters of the log

    if process.returncode == 0:
        await status.edit(content=f'Command "{command}" executed in {elapsed_time:.2f} seconds:')
    else:
        await status.edit(content=f'Error while executing the command "{command}":')

    if log_message:
        await ctx.send(f'```\n{log_message}\n```')

# Function to execute multiple commands and display the status messages and log outputs
async def execute_commands_with_status_messages(ctx, commands):
    for command in commands:
        await execute_command_with_status_message(ctx, command)

# Run the bot with the provided token
bot.run(TOKEN)