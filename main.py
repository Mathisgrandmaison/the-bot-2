import discord
from discord.ext import commands

# Your bot's token and application (client) ID
TOKEN = 'MTMwOTk1NDc4MjY5NzM2MTQ5OA.Gufm8I.pPH21L9mi5y0DVVCLZ238NRtsUHlZwRzcAewz0'
CLIENT_ID = '1309954782697361498'

# Intents and bot setup
intents = discord.Intents.default()
intents.members = True  # Enable member intents for moderation commands
intents.message_content = True  # Ensure the bot can read message content
bot = commands.Bot(command_prefix="!", intents=intents)

# The channel ID you want the bot to listen to
TARGET_CHANNEL_ID = 1309957950852304978

# List of admin role IDs to mention
ADMIN_ROLE_IDS = [1309962952027148288, 1284994415563374662]  # Replace with actual admin role IDs

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()  # Synchronize the slash commands with Discord
        print(f"Bot is online as {bot.user} and commands are synced!")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.event
async def on_message(message):
    if message.channel.id == TARGET_CHANNEL_ID:
        # React with the star and warning emojis
        await message.add_reaction('⭐')
        await message.add_reaction('⚠️')

        # Periodically check the reactions
        async def check_reactions():
            await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=10))  # Check after 10 seconds
            # Fetch the updated message
            message_updated = await message.channel.fetch_message(message.id)
            reactions = {str(reaction.emoji): reaction.count for reaction in message_updated.reactions}

            # Get reaction counts
            stars = reactions.get('⭐', 0)
            warnings = reactions.get('⚠️', 0)

            if warnings >= 20:
                if stars < warnings:
                    await message.delete()
                else:
                    # Mention admins
                    admin_mentions = " ".join([f"<@&{role_id}>" for role_id in ADMIN_ROLE_IDS])
                    await message.reply(f"Attention: {admin_mentions}. This suggestion has received 20 ⚠️ warnings but enough ⭐ to stay.")

        bot.loop.create_task(check_reactions())

    # Ensure other commands still work
    await bot.process_commands(message)

# Slash command: /kick
@bot.tree.command(name="kick", description="Kick a member from the server.")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("You don't have permission to kick members.", ephemeral=True)
        return

    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"{member} has been kicked. Reason: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to kick {member}. Error: {e}", ephemeral=True)

# Slash command: /ban
@bot.tree.command(name="ban", description="Ban a member from the server.")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("You don't have permission to ban members.", ephemeral=True)
        return

    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"{member} has been banned. Reason: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to ban {member}. Error: {e}", ephemeral=True)

# Slash command: /mute
@bot.tree.command(name="mute", description="Mute a member in the server.")
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("You don't have permission to mute members.", ephemeral=True)
        return

    try:
        duration = discord.utils.utcnow() + discord.utils.timedelta(minutes=10)  # Default 10 minutes mute
        await member.timeout(duration, reason=reason)
        await interaction.response.send_message(f"{member} has been muted for 10 minutes. Reason: {reason}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to mute {member}. Error: {e}", ephemeral=True)

# Start the bot
bot.run(TOKEN)
