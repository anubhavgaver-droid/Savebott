# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import motor.motor_asyncio
from config import DB_NAME, DB_URI
import time

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            session = None,
            api_id = None,
            api_hash = None,
            chat_id = None,
            thumbnail = None,
            caption = None,
            artist = None,
            used_bytes = 0,
            plan = "free",          # 'free', 'basic', 'standard', 'pro'
            plan_expiry = 0,        # Expiry timestamp
            daily_files = 0,        # Aaj ki download count
            last_reset = 0          # 24 hours timer check
        )
    
    async def add_user(self, id, name):
        if not await self.is_user_exist(id):
            user = self.new_user(id, name)
            await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('session') if user else None

    async def remove_session(self, id):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': None}})

    async def set_api_id(self, id, api_id):
        await self.col.update_one({'id': int(id)}, {'$set': {'api_id': api_id}})

    async def get_api_id(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('api_id') if user else None

    async def set_api_hash(self, id, api_hash):
        await self.col.update_one({'id': int(id)}, {'$set': {'api_hash': api_hash}})

    async def get_api_hash(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('api_hash') if user else None

    # Channel / Chat Settings
    async def set_chat(self, id, chat_id):
        await self.col.update_one({'id': int(id)}, {'$set': {'chat_id': chat_id}})

    async def get_chat(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('chat_id') if user else None

    # Thumbnail Settings
    async def set_thumbnail(self, id, thumbnail):
        await self.col.update_one({'id': int(id)}, {'$set': {'thumbnail': thumbnail}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('thumbnail') if user else None

    # Custom Caption Settings
    async def set_caption(self, id, caption):
        await self.col.update_one({'id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('caption') if user else None

    # Custom Artist Settings
    async def set_artist(self, id, artist):
        await self.col.update_one({'id': int(id)}, {'$set': {'artist': artist}})

    async def get_artist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('artist') if user else None

    # Usage & Plan Database Methods
    async def get_user_data(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user if user else None

    async def set_user_plan(self, id, plan_name, expiry_seconds):
        expiry_time = time.time() + expiry_seconds if expiry_seconds > 0 else 0
        await self.col.update_one(
            {'id': int(id)}, 
            {'$set': {'plan': plan_name, 'plan_expiry': expiry_time}}
        )

    async def add_used_bytes(self, id, bytes_count):
        user = await self.col.find_one({'id': int(id)})
        current = user.get('used_bytes', 0) if user else 0
        await self.col.update_one({'id': int(id)}, {'$set': {'used_bytes': current + bytes_count}})

    async def get_used_bytes(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('used_bytes', 0) if user else 0

    async def check_and_update_limit(self, id, file_size):
        user = await self.col.find_one({'id': int(id)})
        if not user:
            return False, "User not found. Please /start the bot."

        current_time = time.time()
        
        # Plan Expiry Check
        plan = user.get('plan', 'free')
        expiry = user.get('plan_expiry', 0)
        if plan != 'free' and expiry > 0 and current_time > expiry:
            plan = 'free'
            await self.col.update_one({'id': int(id)}, {'$set': {'plan': 'free', 'plan_expiry': 0}})

        last_reset = user.get('last_reset', 0)
        daily_files = user.get('daily_files', 0)

        # 24 Hours Reset Logic
        if current_time - last_reset >= 86400:
            daily_files = 0
            last_reset = current_time

        # Plan-wise Limits Configuration
        if plan == "free":
            max_files = 40
            max_size_mb = 40
            max_total_mb = 500      # Free total limit 500 MB
        elif plan == "basic":
            max_files = 100
            max_size_mb = 100
            max_total_mb = 1500     # Basic total limit 1500 MB
        elif plan == "standard":
            max_files = 300
            max_size_mb = 500
            max_total_mb = 5000     # Standard total limit 5000 MB
        elif plan == "pro":
            max_files = 999999      # Unlimited
            max_size_mb = 4000
            max_total_mb = 99999999 # Pro unlimited
        else:
            max_files = 40
            max_size_mb = 40
            max_total_mb = 500

        # File Size Check per file
        file_size_mb = file_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return False, f"❌ File size exceeds! Your current plan allows max {max_size_mb} MB per file."

        # Total Data Usage Check
        current_used_mb = user.get('used_bytes', 0) / (1024 * 1024)
        if (current_used_mb + file_size_mb) > max_total_mb:
            return False, f"❌ Plan Data Limit Exceeded! Your plan allows total {max_total_mb} MB usage."

        # Daily Files Count Check
        if daily_files >= max_files:
            return False, f"❌ Daily file limit reached ({max_files} files/day). Please upgrade your plan or wait 24 hours."

        # Update Counters
        await self.col.update_one(
            {'id': int(id)}, 
            {'$set': {'daily_files': daily_files + 1, 'last_reset': last_reset}}
        )
        return True, "Allowed"

db = Database(DB_URI, "TechVJDemoBot")
