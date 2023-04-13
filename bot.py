import time
import responses
import discord
last_request_time = {}
import asyncio
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from googletrans import Translator

# Create an instance of the translator
translator = Translator()
nltk.download('vader_lexicon')  # Tải dữ liệu cho SentimentIntensityAnalyzer

# Tạo một đối tượng SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()
messagess = []

passwords = {  # Tạo một dictionary để lưu trữ thông tin mật khẩu của người dùng.
    "username1": "password1",
    "username2": "password2",
    "username3": "password3"
}

# Thiết lập giá trị điểm ban đầu cho tất cả các người dùng.

async def send_message(message, user_message, username, is_private):
    try:
        response = responses.get_response(user_message, username)
        await message.author.send(response) if is_private else await message.channel.send(response)

    except Exception as e:
        print(e)


def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    balances = {}  # Tạo một dictionary để lưu trữ điểm của người dùng.
    login = {}
    account = {}
    @client.event
    async def on_ready():
        print(client.guilds[0].members)
        print(f'{client.user} is now running!')

    @client.event
    async def handle_confirmation(user, check_func, timeout):
        try:
            msg = await client.wait_for('message', check=check_func, timeout=timeout)
            return msg
        except asyncio.TimeoutError:
            return None

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{user_message}" ({channel})')


        if user_message[0] == '?':
            user_message = user_message[1:]
            await send_message(message, user_message, username, is_private=True)
        else:
            await send_message(message, user_message, username, is_private=False)

        if user_message.startswith('!login '):  # Kiểm tra nếu tin nhắn bắt đầu bằng '?login'.
            username_0 = user_message.split()[1]  # Lấy tên người dùng từ tin nhắn.
            if username_0 in passwords:
                if username not in login:
                    login.setdefault(username, 0)
                if login[username] == 0:
                    dm_channel = await message.author.create_dm()  # tạo kênh riêng tư giữa bot và người dùng
                    await dm_channel.send("Nhập mật khẩu để đăng nhập.")  # yêu cầu nhập mật khẩu qua kênh riêng tư

                    def check_password(m):
                        return m.author == message.author and isinstance(m.content, str) and m.content == passwords[
                            username_0]

                    try:
                        await client.wait_for('message', check=check_password,
                                                           timeout=60.0)  # chờ người dùng nhập mật khẩu
                        await dm_channel.send("Đăng nhập thành công!")
                        login[username] = 1
                        account[username] = username_0
                    except:
                        await dm_channel.send("Đăng nhập ngu")
                elif login[username] == 1:
                    dm_channel = await message.author.create_dm()
                    msg = await dm_channel.send(f"You are already logged in"
                                          f"If you want to log in as a different user, please log out first ")
                    await msg.add_reaction('✅')  # Add checkmark reaction to the message

                    def check(reaction, user):
                        return user != client.user and str(reaction.emoji) == '✅'

                    try:
                        await client.wait_for('reaction_add', check=check, timeout=60.0)
                        # Chờ người dùng phản hồi bằng cách tích vào emoji.
                        await dm_channel.send("Please enter your password to log in.")

                        def check(m):
                            return m.author == message.author and isinstance(m.content, str) and m.content == passwords[username]
                        try:
                            await client.wait_for('message', check=check, timeout=60.0)
                            await dm_channel.send("Logged in successfully!")
                            login[username] = 1
                        except:
                            await dm_channel.send("Failed to log in.")
                    except:
                        await dm_channel.send("Timed out waiting for your response.")

            else:
                await message.author.send("Tên người dùng không tồn tại.")  # Gửi tin nhắn riêng tư thông báo tên người dùng không tồn tại.

        if user_message.startswith('^'):
            await message.author.send(login)
            await message.author.send(account)
            await message.author.send(balances)
        if "cần tiền" in user_message:
            if username not in login:
                response_message = "Please login first"
                await message.author.send(response_message)
            elif login[username] == 0:
                response_message = "Please login first"
                await message.author.send(response_message)
            else:
                current_time = time.time()
                if username in last_request_time and current_time - last_request_time[username] < 300:
                    response_message = "Bạn phải đợi ít nhất 5 phút trước khi yêu cầu tiếp theo."
                    await message.author.send(response_message)
                else:
                    last_request_time[username] = current_time
                    response_message = f"{message.author.name} cần tiền! 🟢"
                    sent_message = await message.channel.send(response_message)
                    await sent_message.add_reaction('✅')  # Add checkmark reaction to the message

                    def check(reaction, user):
                        return user != client.user and str(reaction.emoji) == '✅'
                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=60.0,
                                                               check=check)  # Wait for the reaction from the user for 60 seconds
                        user_name = str(user.name) + '#' + str(user.discriminator)
                        if user_name not in login:
                            response_private_message = user_name
                            await user.send(response_private_message)  # Send the private message to the user who reacted
                        if login[user_name] == 0:
                            response_private_message = "Please log in first"
                            await user.send(response_private_message)  # Send the private message to the user who reacted
                        else:
                            response_private_message = "Bạn cần chuyển bao nhiêu?"
                            await user.send(response_private_message)  # Send the private message to the user who reacted
                            def check_var(m):
                                if m.author == user and m.content.isdigit():
                                    return m
                            try:
                                msg = await client.wait_for('message', check=check_var, timeout=60.0)
                                user_name = str(user.name) + '#' + str(user.discriminator)
                                if account[user_name] not in balances:
                                    balances[account[user_name]] = 10000000
                                if account[username] not in balances:
                                    balances[account[username]] = 10000000
                                response_private_message = "Bạn có chắc muốn chuyển {} tiền đến tài khoản {} không? Nhập 'yes' để đồng ý. Nếu muốn đổi số tiền, nhập 1 số khasc".format(
                                    int(msg.content), account)
                                await user.send(response_private_message)  # Send the confirmation message to the user who reacted

                                try:
                                    confirmation = await client.wait_for('message', timeout=60.0)
                                    await user.send(confirmation.content)
                                    if confirmation.content == 'yes':
                                        balances[account[user_name]] -= int(msg.content)
                                        balances[account[username]] += int(msg.content)
                                        await user.send(user_name)
                                        await user.send(username)
                                        await user.send(balances[account[user_name]])
                                        await user.send(balances[account[username]])
                                    else:
                                            # User entered a different amount
                                        new_amount = int(confirmation.content)
                                        balances[account[user_name]] -= new_amount
                                        balances[account[username]] += new_amount
                                        await user.send(user_name)
                                        await user.send(username)
                                        await user.send(balances[account[user_name]])
                                        await user.send(balances[account[username]])
                                except asyncio.TimeoutError:
                                    await user.send('Timed out. Please try again.')
                            except:
                                await user.send('-_-')
                    except:
                        pass  # If the user doesn't react in 60 seconds, do nothing
        if user_message[0] == 'v':
            user_message = user_message[1:]
            translation = translator.translate(user_message)
            scores = sia.polarity_scores(translation.text)
            dm_channel = await message.author.create_dm()
            await dm_channel.send(scores)
        if 'chuyển tiền' in user_message:
            dm_channel = await message.author.create_dm()
            await dm_channel.send("Bạn muốn chuyển tiền cho ai")

            try:
                msg = await client.wait_for('message', timeout=60.0)  # chờ người dùng nhập mật khẩu
                await dm_channel.send(msg.content)
                await dm_channel.send("Số tiền bạn muốn chuyển")
                try:
                    msg2 = await client.wait_for('message', timeout=60.0)  # chờ người dùng nhập mật khẩu
                    await dm_channel.send(int(msg2.content))
                    await dm_channel.send(msg.content)
                    response_private_message = "Bạn có chắc muốn chuyển {} tiền đến tài khoản {} không? Nhập 'yes' để đồng ý.".format(
                        int(msg.content), account)
                    await dm_channel(response_private_message)  # Send the confirmation message to the user who reacted

                    def check_confirmation(m):
                        return m.author == user and m.content.lower() == 'yes'

                    try:
                        await client.wait_for('message', check=check_confirmation,
                                              timeout=60.0)
                        balances[account[msg.content]] -= int(msg2.content)
                        balances[account[username]] += int(msg2.content)
                    except:
                        await dm_channel.send('-_-')
                except:
                    await dm_channel.send('-_-')
            except:
                await message.author.send("Tên người dùng không tồn tại.")


    # Remember to run your bot with your personal TOKEN
    client.run("MTA5NTI5NDI4OTU0NzkwMzAyNg.GnPLK7.5lUH4LhUDyJR0c3OWuTGJsOgXV9LVwtpgOLmoA")
