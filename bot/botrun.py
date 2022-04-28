import os, sqlite3
import discord
from discord.ext import commands
import string, json

intents=intents=discord.Intents.all()
bot = commands.Bot(command_prefix='-', intents=intents)


#Ивенты на старте и присоединении.
@bot.event
async def on_ready():
	print("Я на месте")

	global base, cursor, base2, cursor2
	base = sqlite3.connect("Бот.db")
	cursor = base.cursor()
	if base:
		print("С Бд все хорошо")
	base2 = sqlite3.connect("students.db")
	cursor2 = base2.cursor()
	if base2:
		print("Со второй БД все норм")


@bot.event
async def on_member_join(member):
	await member.send('Приветствую Вас, чтобы Вы смогли продолжить работу на данном сервере пройдите в канал <получение-ролей> и\n \
		напишите следующее <-ФИО *здесь Ваши Фамилия, имя, отчество*>, если Вы не студент, то обратитесь за помощью к инженерам\n \
		данного сервера. Всего хорошего')

	for i in bot.get_guild(member.guild.id).channels:
		if i.name == "основной":
			await bot.get_channel(i.id).send(f"{member.mention}, Добро Пожаловать, вся нужная информация у Вас в личных сообщениях.")
	role = discord.utils.get(member.guild.roles, name='Студент')        
	await member.add_roles(role)
#/


#Команды не связанные с БД(помощь и группа)
@bot.command()
async def помощь(ctx, *, args=None):
	author = ctx.message.author
	if args == None:
		await ctx.send(f"{author.mention}, я бот, созданный чтобы следить за Вашей речью")
	elif args == "я даун":
		await ctx.send(f"{author.mention}, соболезную")


@bot.command()
async def инфо(ctx):
	await ctx.message.send("Данная разработка была создана Николаем Бушмановым в содружестве с gr.samoxin a.k.a. Григорий Самохин \n \
		студент группы 2-МДА-9. /n Всего хорошего.")
@bot.command()
async def группа(ctx, member: discord.Member, role: discord.Role):
	getrole = discord.utils.get(ctx.guild.roles, id = role.id)
	await member.add_roles(getrole)
#/

#Команды связанные с БД(проверка статуса, обнуление счетчика) Их две
@bot.command()
async def статус(ctx):
	base.execute("""CREATE TABLE IF NOT EXISTS '%{}%'(user_id INT, count INT)""".format(ctx.message.guild.name))
	base.commit()
	warnings = cursor.execute("""SELECT * FROM '%{}%' WHERE user_id == ?""".format(ctx.message.guild.name),\
		(ctx.message.author.id,)).fetchone()
	if warnings == None:
		await ctx.send(f"{ctx.message.author.mention}, у Вас нет нарушений")
	else:	
		await ctx.send(f"{ctx.message.author.mention}, у Вас {warnings[1]} нарушений")


@commands.has_role("Инженер")
@bot.command()
async def обнулить(ctx, arg):
	cursor.execute("""UPDATE '%{}%' SET count = ? WHERE user_id = ?""".format(ctx.message.guild.name), (0, arg))
	base.commit()
#/


#Получение роли на сервере
@bot.command(pass_context=True)
@commands.has_permissions(change_nickname=True)
async def ФИО(ctx, *args, nick=None):
	member = ctx.message.author
	Full_name = args
	Full_name = ' '.join(Full_name)
	NAMES = cursor2.execute("""SELECT Name_of_Group FROM student WHERE Fio = ?""", (Full_name,)).fetchone()
	NAMES = ''.join(NAMES)
	Is_Registred = cursor2.execute("""SELECT Registration FROM student WHERE Fio = ?""", (Full_name,)).fetchone()
	Is_Registred = ''.join(Is_Registred)
	print (Is_Registred)
	if Is_Registred != 'True':
		role = discord.utils.get(bot.get_guild(ctx.guild.id).roles, name = NAMES)
		await member.add_roles(role)
		try:
			nick = Full_name
			await member.edit(nick=nick)
		except Exception as e:
			await ctx.send(str(e))
		cursor2.execute("""UPDATE student SET Registration = ? WHERE Fio = ?""", ('True', Full_name,))
		base2.commit()
	else:
		await ctx.send(f"{ctx.message.author.mention}, видимо Вы уже получили Вашу роль, либо возникла ошибка и Вам нужно обратиться к инженерам сервера")
#/

#Реакции и роли
@bot.event
async def on_raw_reaction_add(payload):
	message_id = payload.message_id
	if message_id == 871943332778106911:
		guild = bot.get_guild(payload.guild_id)

		if payload.emoji.name in roles:
			if payload.emoji.name == "🦊":
				role = discord.utils.get(guild.roles, name = "1-МДА-9")
			elif payload.emoji.name == "🐲":
				role = discord.utils.get(guild.roles, name = "2-МДА-9")
			elif payload.emoji.name == "🐻":
				role = discord.utils.get(guild.roles, name = "3-МДА-9")
			elif payload.emoji.name == "🐵":
				role = discord.utils.get(guild.roles, name = "4-МДА-9")
			elif payload.emoji.name == "🦁":
				role = discord.utils.get(guild.roles, name = "1-МДА-7")
			elif payload.emoji.name == "🐱":
				role = discord.utils.get(guild.roles, name = "2-МДА-7")
			elif payload.emoji.name == "🦝":
				role = discord.utils.get(guild.roles, name = "3-МДА-7")
			elif payload.emoji.name == "🐭":
				role = discord.utils.get(guild.roles, name = "4-МДА-7")
			elif payload.emoji.name == "🐹":
				role = discord.utils.get(guild.roles, name = "1-МД-16")
			elif payload.emoji.name == "🐼":
				role = discord.utils.get(guild.roles, name = "2-МД-16")
			elif payload.emoji.name == "🦉":
				role = discord.utils.get(guild.roles, name = "3-МД-16")
			else:
				role = discord.utils.get(guild.roles, name = "4-МД-16")

			if role is not None:
				member = payload.member
				if member is not None:
					await member.add_roles(role)
				else: 
					print("Человек не найден")
			else:
				print("Роль не найдена")


@bot.event
async def on_raw_reaction_remove(payload):
	message_id = payload.message_id
	if message_id == 871943332778106911:
		guild = bot.get_guild(payload.guild_id)

		if payload.emoji.name in roles:
			if payload.emoji.name == "🦊":
				role = discord.utils.get(guild.roles, name = "1-МДА-9")
			elif payload.emoji.name == "🐲":
				role = discord.utils.get(guild.roles, name = "2-МДА-9")
			elif payload.emoji.name == "🐻":
				role = discord.utils.get(guild.roles, name = "3-МДА-9")
			elif payload.emoji.name == "🐵":
				role = discord.utils.get(guild.roles, name = "4-МДА-9")
			elif payload.emoji.name == "🦁":
				role = discord.utils.get(guild.roles, name = "1-МДА-7")
			elif payload.emoji.name == "🐱":
				role = discord.utils.get(guild.roles, name = "2-МДА-7")
			elif payload.emoji.name == "🦝":
				role = discord.utils.get(guild.roles, name = "3-МДА-7")
			elif payload.emoji.name == "🐭":
				role = discord.utils.get(guild.roles, name = "4-МДА-7")
			elif payload.emoji.name == "🐹":
				role = discord.utils.get(guild.roles, name = "1-МД-16")
			elif payload.emoji.name == "🐼":
				role = discord.utils.get(guild.roles, name = "2-МД-16")
			elif payload.emoji.name == "🦉":
				role = discord.utils.get(guild.roles, name = "3-МД-16")
			else:
				role = discord.utils.get(guild.roles, name = "4-МД-16")

			if role is not None:
				member = guild.get_member(payload.user_id)
				if member is not None:
					await member.remove_roles(role)
				else: 
					print("Человек не найден")
			else:
				print("Роль не найдена")
#/


#Основной алгоритм фильтрации текста
@bot.event
async def on_message(message):
	if {i.lower().translate(str.maketrans('','', string.punctuation)) for i in message.content.split(" ")}\
	.intersection(set(json.load(open('cenz.json')))) != set():
			await message.channel.send(f"{message.author.mention}, ты такое не говори, брат")
			
			await message.delete()

			name = message.guild.name

			base.execute("""CREATE TABLE IF NOT EXISTS '%{}%'(user_id INT, count INT)""".format(name))
			base.commit()

			warnings = cursor.execute("""SELECT * FROM '%{}%' WHERE user_id == ?""".format(name), (message.author.id,)).fetchone()

			if warnings == None:
				cursor.execute("""INSERT INTO '%{}%' VALUES(?, ?)""".format(name), (message.author.id, 1))
				base.commit()
				await message.channel.send(f"{message.author.mention}, у Вас первое предупреждение за нецензурную лексику, за 3 таких, Вас замьютит")

			elif warnings[1] == 1:
				cursor.execute("""UPDATE '%{}%' SET count = ? WHERE user_id = ?""".format(name), (2,message.author.id,))
				base.commit()
				await message.channel.send(f"{message.author.mention}, у Вас второе предупреждение за нецензурную лексику, за 3 таких, Вас замьютит")

			elif warnings[1] == 2:
				cursor.execute("""UPDATE '%{}%' SET count = ? WHERE user_id = ?""".format(name), (3,message.author.id,))
				base.commit()
				await message.channel.send(f"{message.author.mention} замьючен за нецензурную лексику")
				await message.author.ban(reason='Нецензурная лексика')

	await bot.process_commands(message)
#/

bot.run(os.getenv('TOKEN'))