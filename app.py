import json
import os
import random
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="Scam Jose Paul Multiplayer League")

ROOMS_FILE = "active_rooms.json"
connected_clients = {}

def load_rooms():
    if not os.path.exists(ROOMS_FILE):
        return {}
    try:
        with open(ROOMS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_rooms(rooms):
    with open(ROOMS_FILE, "w") as f:
        json.dump(rooms, f, indent=4)

async def broadcast_room_state(room_code):
    rooms = load_rooms()
    if room_code not in rooms:
        return
    room = rooms[room_code]
    active_players = list(room["players"].keys())
    payload = json.dumps({"type": "players", "players": active_players})
    if room_code in connected_clients:
        for ws in connected_clients[room_code].values():
            try:
                await ws.send_text(payload)
            except:
                pass

SHOP_ITEMS = {
    "shield": {"name": "Shield", "price": 2500, "category": "Defense", "desc": "Automatically shatters to save your life and wallet from death."},
    "reviver": {"name": "Reviver Token", "price": 1000000, "category": "Defense", "desc": "Ultimate life insurance. Automatically revives you from death."},
    "padlock": {"name": "Padlock", "price": 1500, "category": "Defense", "desc": "Protects your wallet from street muggers."},
    "golden_padlock": {"name": "Golden Padlock", "price": 100000, "category": "Defense", "desc": "Heavy-duty lock that stops advanced robberies."},
    "bank_lock": {"name": "Bank Lock", "price": 50000, "category": "Defense", "desc": "Secures your bank vault from heists."},
    "banknote": {"name": "Banknote", "price": 2000, "category": "Upgrade", "desc": "Increases max bank capacity by 5,000."},
    "fishing_rod": {"name": "Fishing Rod", "price": 2500, "category": "Tool", "desc": "Required to catch sea creatures."},
    "hunting_rifle": {"name": "Hunting Rifle", "price": 3000, "category": "Tool", "desc": "Required to hunt wild beasts."},
    "shovel": {"name": "Shovel", "price": 2500, "category": "Tool", "desc": "Required to dig up buried treasure."},
    "god_box": {"name": "God Box", "price": 500000, "category": "Lootbox", "desc": "Mythical mystery box packed with massive rewards."},
    "meme_card": {"name": "Rare Meme Card", "price": 25000, "category": "Collectible", "desc": "Limited edition holographic meme card."},
    "sister_fahaana": {"name": "Sister Fahaana", "price": 69000, "category": "Collectible", "desc": "A life-size 5'6 pillow of a human. Peak flex."},
}

LOOT_ITEMS = {
    "dragon_scale": {"name": "Dragon Scale", "sell_price": 4500},
    "kong_fur": {"name": "Gorilla Fur Tuft", "sell_price": 3200},
    "yeti_claw": {"name": "Frozen Yeti Claw", "sell_price": 3800},
    "magma_core": {"name": "Volcanic Magma Core", "sell_price": 7500},
    "wolf_fang": {"name": "Alpha Wolf Fang", "sell_price": 2800},
    "trex_tooth": {"name": "Fossilized T-Rex Tooth", "sell_price": 5000},
    "saber_pelt": {"name": "Saber-Tooth Pelt", "sell_price": 2500},
    "venom_stinger": {"name": "Giant Venom Stinger", "sell_price": 2700},
    "phoenix_feather": {"name": "Glowing Phoenix Feather", "sell_price": 6500},
    "zombie_brain": {"name": "Preserved Zombie Brain", "sell_price": 2000},
    "mammoth_tusk": {"name": "Ivory Mammoth Tusk", "sell_price": 3600},
    "hydra_head": {"name": "Severed Hydra Head", "sell_price": 6000},
    "boar_hide": {"name": "Tough Boar Hide", "sell_price": 2100},
    "vampire_cape": {"name": "Crimson Vampire Cape", "sell_price": 4800},
    "oni_mask": {"name": "Cursed Oni Mask", "sell_price": 8500},
    "shark_fin": {"name": "Great White Fin", "sell_price": 3000},
    "kraken_ink": {"name": "Cosmic Kraken Ink", "sell_price": 6500},
    "leviathan_pearl": {"name": "Abyssal Leviathan Pearl", "sell_price": 7200},
    "megalodon_jaw": {"name": "Colossal Megalodon Jaw", "sell_price": 5800},
    "siren_tear": {"name": "Crystallized Siren Tear", "sell_price": 4000},
    "crab_shell": {"name": "Reinforced King Crab Shell", "sell_price": 2400},
    "eel_battery": {"name": "Bio-Electric Eel Gland", "sell_price": 3300},
    "gator_leather": {"name": "Ancient Swamp Gator Skin", "sell_price": 3500},
    "squid_tentacle": {"name": "Giant Squid Tentacle", "sell_price": 4900},
    "ancient_shell": {"name": "Prehistoric Turtle Shell", "sell_price": 2200},
    "hammerhead_skull": {"name": "Hammerhead Trophy Skull", "sell_price": 3100},
    "ghost_compass": {"name": "Cursed Phantom Compass", "sell_price": 9500},
    "vortex_shard": {"name": "Deep Sea Vortex Shard", "sell_price": 6200},
    "puffer_toxin": {"name": "Rare Pufferfish Toxin", "sell_price": 2600},
    "water_dragon_orb": {"name": "Jade Water Dragon Orb", "sell_price": 8000},
    "teller_stamp": {"name": "Official Teller Stamp", "sell_price": 3500},
    "cashier_badge": {"name": "Golden Cashier Badge", "sell_price": 5500},
    "vault_keycard": {"name": "Encrypted Vault Keycard", "sell_price": 9000},
    "manager_rolex": {"name": "Manager Karthik's Fake Rolex", "sell_price": 14000},
    "invingoppa_ledger": {"name": "INVINGOPPA's Secret Black Ledger", "sell_price": 35000},
}

JOBS = {
    "moderator": {"name": "Meme Moderator", "pay": (150, 400), "req_level": 1, "desc": "Keep server clean."},
    "street_magician": {"name": "Street Magician", "pay": (200, 600), "req_level": 1, "desc": "Card tricks."},
    "trash_collector": {"name": "Trash Collector", "pay": (300, 750), "req_level": 1, "desc": "Recycle electronics."},
    "stray_feeder": {"name": "Cat Feeder", "pay": (500, 1200), "req_level": 1, "desc": "Feed stray cats."},
    "streamer": {"name": "Twitch Streamer", "pay": (400, 900), "req_level": 2, "desc": "Play dank games."},
    "fast_food": {"name": "Fry Cook", "pay": (450, 950), "req_level": 2, "desc": "Flip burgers."},
    "delivery_driver": {"name": "Delivery Driver", "pay": (600, 1200), "req_level": 2, "desc": "Deliver food."},
    "barista": {"name": "Barista", "pay": (800, 1500), "req_level": 2, "desc": "Spell names wrong."},
    "miner": {"name": "Crypto Miner", "pay": (900, 1800), "req_level": 3, "desc": "Mine Dogecoin."},
    "discord_admin": {"name": "Discord Admin", "pay": (1000, 2000), "req_level": 3, "desc": "Ban light mode."},
    "tiktok_influencer": {"name": "NPC Streamer", "pay": (1200, 2500), "req_level": 3, "desc": "Ice cream so good."},
    "street_artist": {"name": "Graffiti Artist", "pay": (1500, 3200), "req_level": 4, "desc": "Paint murals."},
    "hacker": {"name": "Dark Web Hacker", "pay": (1800, 3500), "req_level": 4, "desc": "Steal data."},
    "ceo": {"name": "Tech CEO", "pay": (3500, 7000), "req_level": 5, "desc": "Run tech firm."},
    "stunt_double": {"name": "Stunt Double", "pay": (3500, 7000), "req_level": 5, "desc": "Jump off buildings."},
    "scam_caller": {"name": "Scam Caller", "pay": (4000, 8000), "req_level": 6, "desc": "Computer has virus."},
    "ghost_hunter": {"name": "Ghost Hunter", "pay": (4000, 8500), "req_level": 6, "desc": "Hunt poltergeists."},
    "cryptid_wrangler": {"name": "Cryptid Wrangler", "pay": (5000, 9000), "req_level": 7, "desc": "Catch Bigfoot."},
    "ponzi_boss": {"name": "Ponzi Architect", "pay": (7500, 12000), "req_level": 7, "desc": "Fake crypto."},
    "bounty_hunter": {"name": "Bounty Hunter", "pay": (5000, 10000), "req_level": 8, "desc": "Track fugitives."},
    "ai_trainer": {"name": "Prompt Engineer", "pay": (6000, 11000), "req_level": 8, "desc": "Write python code."},
    "bodyguard": {"name": "VIP Bodyguard", "pay": (6500, 13000), "req_level": 9, "desc": "Take bullets."},
    "dj_producer": {"name": "Festival DJ", "pay": (8500, 15000), "req_level": 9, "desc": "Press play."},
    "quantum_physicist": {"name": "Quantum Physicist", "pay": (12000, 20000), "req_level": 10, "desc": "Open portals."},
    "dark_web_arms": {"name": "Arms Dealer", "pay": (15000, 25000), "req_level": 12, "desc": "Sell memes."},
    "meme_lord": {"name": "Supreme Meme Lord", "pay": (20000, 35000), "req_level": 15, "desc": "Control trends."},
    "casino_pit_boss": {"name": "Casino Pit Boss", "pay": (25000, 45000), "req_level": 16, "desc": "House wins."},
    "galactic_smuggler": {"name": "Galactic Smuggler", "pay": (30000, 50000), "req_level": 18, "desc": "Smuggle Pepes."},
    "time_traveller": {"name": "Time Trader", "pay": (45000, 75000), "req_level": 20, "desc": "Buy stocks yesterday."},
    "matrix_architect": {"name": "Matrix Architect", "pay": (70000, 100000), "req_level": 25, "desc": "Rewrite simulation."},
}

HUNT_BOSSES = [
    {"name": "🐉 Dragon", "reward": 15000, "risk": 0.45, "drop": "dragon_scale"},
    {"name": "🦍 Gorilla", "reward": 12000, "risk": 0.38, "drop": "kong_fur"},
    {"name": "🧊 Yeti", "reward": 14000, "risk": 0.40, "drop": "yeti_claw"},
    {"name": "🌋 Titan", "reward": 25000, "risk": 0.55, "drop": "magma_core"},
    {"name": "🐺 Werewolf", "reward": 11000, "risk": 0.35, "drop": "wolf_fang"},
    {"name": "🦖 T-Rex", "reward": 18000, "risk": 0.48, "drop": "trex_tooth"},
    {"name": "🐅 Tiger", "reward": 9500, "risk": 0.30, "drop": "saber_pelt"},
    {"name": "🦂 Crawler", "reward": 10500, "risk": 0.32, "drop": "venom_stinger"},
    {"name": "🦅 Phoenix", "reward": 22000, "risk": 0.50, "drop": "phoenix_feather"},
    {"name": "🧟 Zombies", "reward": 8000, "risk": 0.28, "drop": "zombie_brain"},
    {"name": "🦣 Mammoth", "reward": 13000, "risk": 0.39, "drop": "mammoth_tusk"},
    {"name": "🐍 Hydra", "reward": 20000, "risk": 0.52, "drop": "hydra_head"},
    {"name": "🐗 Boar", "reward": 8500, "risk": 0.29, "drop": "boar_hide"},
    {"name": "🦇 Vampire", "reward": 16000, "risk": 0.44, "drop": "vampire_cape"},
    {"name": "👹 Oni", "reward": 28000, "risk": 0.60, "drop": "oni_mask"},
]

FISH_BOSSES = [
    {"name": "🦈 Shark", "reward": 10000, "risk": 0.35, "drop": "shark_fin"},
    {"name": "🐙 Kraken", "reward": 22000, "risk": 0.52, "drop": "kraken_ink"},
    {"name": "🌊 Leviathan", "reward": 24000, "risk": 0.55, "drop": "leviathan_pearl"},
    {"name": "🐋 Megalodon", "reward": 19000, "risk": 0.48, "drop": "megalodon_jaw"},
    {"name": "🧜 Siren", "reward": 14000, "risk": 0.40, "drop": "siren_tear"},
    {"name": "🦀 Crab", "reward": 9000, "risk": 0.30, "drop": "crab_shell"},
    {"name": "⚡ Eel", "reward": 11500, "risk": 0.36, "drop": "eel_battery"},
    {"name": "🐊 Alligator", "reward": 12500, "risk": 0.38, "drop": "gator_leather"},
    {"name": "🦑 Squid", "reward": 17000, "risk": 0.45, "drop": "squid_tentacle"},
    {"name": "🐢 Turtle", "reward": 8500, "risk": 0.28, "drop": "ancient_shell"},
    {"name": "🦈 Hammerhead", "reward": 10500, "risk": 0.33, "drop": "hammerhead_skull"},
    {"name": "👻 Ghost Ship", "reward": 30000, "risk": 0.65, "drop": "ghost_compass"},
    {"name": "🌀 Vortex", "reward": 21000, "risk": 0.50, "drop": "vortex_shard"},
    {"name": "🐡 Puffer", "reward": 9500, "risk": 0.31, "drop": "puffer_toxin"},
    {"name": "🐉 Water Dragon", "reward": 26000, "risk": 0.58, "drop": "water_dragon_orb"},
]

BANK_CLERKS = [
    {"tier": "Mid-Level Clerk", "name": "🧾 Junior Teller Ramesh", "reward": 8000, "risk": 0.30, "drop": "teller_stamp", "weight": 30},
    {"tier": "Mid-Level Clerk", "name": "💳 Senior Cashier Priya", "reward": 14000, "risk": 0.40, "drop": "cashier_badge", "weight": 25},
    {"tier": "Mid-Level Clerk", "name": "📑 Loan Officer Suresh", "reward": 22000, "risk": 0.50, "drop": "vault_keycard", "weight": 20},
    {"tier": "Mid-Level Clerk", "name": "🕴️ Branch Manager Karthik", "reward": 32000, "risk": 0.58, "drop": "manager_rolex", "weight": 15},
    {"tier": "FINAL BOSS", "name": "👑 THE BANK CLERK: INVINGOPPA", "reward": 75000, "risk": 0.72, "drop": "invingoppa_ledger", "weight": 10},
]

def get_user_in_room(room_data, username):
    default_inv = {k: 0 for k in SHOP_ITEMS}
    default_loot = {k: 0 for k in LOOT_ITEMS}
    if username not in room_data["players"]:
        room_data["players"][username] = {
            "wallet": 500, "bank": 0, "bank_max": 5000,
            "level": 1, "xp": 0, "job": "moderator",
            "dead": False, "prison_end": 0,
            "inventory": default_inv, "loot": default_loot
        }
    else:
        u = room_data["players"][username]
        for k in default_inv:
            if k not in u["inventory"]: u["inventory"][k] = 0
        for k in default_loot:
            if k not in u["loot"]: u["loot"][k] = 0
    return room_data["players"][username]

def add_xp(u, amount):
    u["xp"] += amount
    xp_needed = u["level"] * 300
    if u["xp"] >= xp_needed:
        u["level"] += 1
        u["xp"] = 0
        u["bank_max"] += 2500
        bonus = u["level"] * 500
        u["wallet"] += bonus
        return f"🎉 LEVEL UP! Level {u['level']}! Bonus: 🪙 {bonus:,} Coins & +2,500 Bank Space!"
    return None

def handle_death(u):
    if u["inventory"]["shield"] > 0:
        u["inventory"]["shield"] -= 1
        return False, "🛡️ SHIELD SAVED YOU! Your Shield shattered and saved your life!"
    elif u["inventory"]["reviver"] > 0:
        u["inventory"]["reviver"] -= 1
        return False, "✨ REVIVER TOKEN ACTIVATED! Instantly resurrected with zero losses!"
    else:
        u["wallet"] = 0
        u["dead"] = True
        return True, f"💀 FATAL END! All wallet coins lost! Type `revive`."

def check_status(u):
    if u["dead"]:
        return False, "💀 You are DEAD! Type `revive` or buy a Reviver Token."
    if time.time() < u["prison_end"]:
        rem = int(u["prison_end"] - time.time())
        return False, f"🚨 You are in Prison! Wait {rem}s."
    return True, ""

async def process_command(room_code, username, cmd_line):
    rooms = load_rooms()
    if room_code not in rooms:
        return "❌ Room does not exist."
    room = rooms[room_code]
    if not room["active"]:
        return "❌ This league has ended by the host."

    u = get_user_in_room(room, username)
    cmd_text = cmd_line.strip()
    if not cmd_text: return ""

    # HANDLE WHISPER: /whisper <user> <msg>
    if cmd_text.lower().startswith("/whisper "):
        parts = cmd_text.split(" ", 2)
        if len(parts) < 3:
            return "❌ Usage: `/whisper <username> <message>`"
        target_name = parts[1]
        whisper_msg = parts[2]
        
        if target_name not in room["players"]:
            return f"❌ Player '{target_name}' not found in room."
        
        target_ws = connected_clients.get(room_code, {}).get(target_name)
        if target_ws:
            try:
                await target_ws.send_text(f"💬 [WHISPER from {username}]: {whisper_msg}")
            except:
                pass
        return f"💬 [WHISPER to {target_name}]: {whisper_msg}"

    game_commands = ["help", "bal", "balance", "bag", "inv", "inventory", "shop", "buy", "dep", "with", "withdraw", "work", "beg", "dig", "postmemes", "scam", "crime", "hunt", "fish", "bank_heist", "rob", "donate", "revive", "sell", "leaderboard", "lb"]
    
    parts = cmd_text.split()
    cmd = parts[0].lower()
    args = parts[1:]

    # HANDLE PUBLIC CHAT
    if cmd not in game_commands and not cmd_text.startswith("/"):
        chat_msg = f"💬 [{username}]: {cmd_text}"
        if room_code in connected_clients:
            for ws in connected_clients[room_code].values():
                try:
                    await ws.send_text(chat_msg)
                except:
                    pass
        return ""

    response = ""

    if cmd == "help":
        response = """================ 🎮 SCAM JOSE PAUL HELP ================
  bal / balance        - Check profile & net worth
  bag / inv            - View inventory & boss drops
  shop / buy <item>    - Browse and buy items
  dep <amt>/all        - Deposit to bank
  with <amt>/all       - Withdraw from bank
  work                 - Earn salary & XP
  beg, dig, postmemes  - Hustle for cash
  scam, crime          - Risky crimes
  hunt, fish           - Boss raids (15 each)
  bank_heist           - Raid Bank Clerks & INVINGOPPA
  rob <user>           - Steal coins from another player
  donate <user> <amt>  - Send coins to another player
  revive <user>        - Revive a dead friend
  sell <item>/all      - Sell boss drops on market
  leaderboard / lb     - View room rankings
  /whisper <user> <msg>- Secret chat
======================================================="""

    elif cmd in ["bal", "balance"]:
        inv_v = sum(u["inventory"][k] * SHOP_ITEMS[k]["price"] for k in u["inventory"])
        loot_v = sum(u["loot"][k] * LOOT_ITEMS[k]["sell_price"] for k in u["loot"])
        nw = u["wallet"] + u["bank"] + inv_v + loot_v
        status = "DEAD" if u["dead"] else ("PRISON" if time.time() < u["prison_end"] else "Alive")
        response = f"""📊 {username}'s Profile:
⭐ Level: {u['level']} (XP: {u['xp']}) | Status: {status}
💼 Job: {JOBS.get(u['job'], {}).get('name', 'None')}
🪙 Wallet: {u['wallet']:,} | 🏦 Bank: {u['bank']:,} / {u['bank_max']:,}
💎 Net Worth: {nw:,} Coins"""

    elif cmd in ["bag", "inv", "inventory"]:
        gear = [f"{SHOP_ITEMS[k]['name']} (`{k}`): {v}x" for k, v in u["inventory"].items() if v > 0]
        loot = [f"{LOOT_ITEMS[k]['name']} (`{k}`): {v}x" for k, v in u["loot"].items() if v > 0]
        response = f"""🎒 {username}'s Bag:
🛠️ Gear: {', '.join(gear) if gear else 'Empty'}
🏆 Boss Loot: {', '.join(loot) if loot else 'None'}"""

    elif cmd == "shop":
        response = "🛍️ SHOP ITEMS:\n" + "\n".join([f"[{k}] {v['name']} - 🪙 {v['price']:,} ({v['desc']})" for k, v in SHOP_ITEMS.items()])

    elif cmd == "buy":
        ok, msg = check_status(u)
        if not ok: return msg
        if not args: return "❌ Usage: `buy <item>`"
        item = args[0].lower()
        if item not in SHOP_ITEMS: return "❌ Item not found."
        cost = SHOP_ITEMS[item]["price"]
        if u["wallet"] < cost: return f"❌ Need 🪙 {cost:,} in wallet."
        u["wallet"] -= cost
        if item == "banknote":
            u["bank_max"] += 5000
            response = "✅ Purchased Banknote! Max bank +5,000."
        else:
            u["inventory"][item] += 1
            response = f"✅ Purchased 1x {SHOP_ITEMS[item]['name']}!"

    elif cmd == "dep":
        ok, msg = check_status(u)
        if not ok: return msg
        if not args: return "❌ Usage: `dep <amt>` or `dep all`"
        amt = u["wallet"] if args[0].lower() == "all" else int(args[0])
        amt = min(amt, u["bank_max"] - u["bank"])
        if amt <= 0: return "❌ Bank is full or invalid amount."
        u["wallet"] -= amt
        u["bank"] += amt
        response = f"✅ Deposited 🪙 {amt:,} to bank."

    elif cmd in ["with", "withdraw"]:
        ok, msg = check_status(u)
        if not ok: return msg
        if not args: return "❌ Usage: `with <amt>` or `with all`"
        amt = u["bank"] if args[0].lower() == "all" else int(args[0])
        if amt <= 0 or amt > u["bank"]: return "❌ Invalid amount."
        u["bank"] -= amt
        u["wallet"] += amt
        response = f"✅ Withdrew 🪙 {amt:,} to wallet."

    elif cmd == "work":
        ok, msg = check_status(u)
        if not ok: return msg
        j = JOBS.get(u["job"], JOBS["moderator"])
        pay = random.randint(j["pay"][0], j["pay"][1])
        u["wallet"] += pay
        lvl_msg = add_xp(u, 60)
        response = f"💼 Worked as {j['name']} and earned 🪙 {pay:,}!"
        if lvl_msg: response += f"\n{lvl_msg}"

    elif cmd == "beg":
        ok, msg = check_status(u)
        if not ok: return msg
        earned = random.randint(50, 350)
        u["wallet"] += earned
        response = f"🤲 Begged and received 🪙 {earned:,}!"

    elif cmd == "dig":
        ok, msg = check_status(u)
        if not ok: return msg
        if u["inventory"]["shovel"] <= 0: return "❌ You need a Shovel!"
        loot = random.randint(400, 1800)
        u["wallet"] += loot
        response = f"⛏️ Dug up treasure worth 🪙 {loot:,}!"

    elif cmd == "postmemes":
        ok, msg = check_status(u)
        if not ok: return msg
        payout = random.randint(50, 2500)
        u["wallet"] += payout
        response = f"📱 Posted viral meme and earned 🪙 {payout:,}!"

    elif cmd == "scam":
        ok, msg = check_status(u)
        if not ok: return msg
        if random.random() < 0.4:
            fine = random.randint(500, 2000)
            u["wallet"] = max(0, u["wallet"] - fine)
            response = f"🚨 Scammed failed! Fined 🪙 {fine:,}."
        else:
            loot = random.randint(2000, 7000)
            u["wallet"] += loot
            response = f"💻 Scam success! Made 🪙 {loot:,}!"

    elif cmd == "crime":
        ok, msg = check_status(u)
        if not ok: return msg
        if random.random() < 0.15:
            if u["inventory"]["padlock"] > 0:
                u["inventory"]["padlock"] -= 1
                return "🔒 Padlock broke and stopped a mugger!"
            loss = min(u["wallet"], 500)
            u["wallet"] -= loss
            return f"💸 Mugged! Lost 🪙 {loss:,}."
        outcome = random.choices(["success", "fine", "prison", "death"], weights=[40, 25, 20, 15], k=1)[0]
        if outcome == "success":
            loot = random.randint(1500, 5000)
            u["wallet"] += loot
            response = f"🟢 Crime success! Stole 🪙 {loot:,}!"
        elif outcome == "fine":
            u["wallet"] = max(0, u["wallet"] - 1000)
            response = "🟠 Busted by police! Fined 🪙 1,000."
        elif outcome == "prison":
            u["prison_end"] = time.time() + 30
            response = "🚨 Sent to prison for 30s!"
        else:
            dead, death_msg = handle_death(u)
            response = death_msg

    elif cmd == "hunt":
        ok, msg = check_status(u)
        if not ok: return msg
        if u["inventory"]["hunting_rifle"] <= 0: return "❌ Need a Hunting Rifle!"
        boss = random.choice(HUNT_BOSSES)
        if random.random() > (boss["risk"] - 0.15):
            u["wallet"] += boss["reward"]
            u["loot"][boss["drop"]] += 1
            response = f"🏹 Victory! Hunted {boss['name']} for 🪙 {boss['reward']:,} & dropped {LOOT_ITEMS[boss['drop']]['name']}!"
        else:
            dead, death_msg = handle_death(u)
            response = f"💥 Mauled by {boss['name']}! {death_msg}"

    elif cmd == "fish":
        ok, msg = check_status(u)
        if not ok: return msg
        if u["inventory"]["fishing_rod"] <= 0: return "❌ Need a Fishing Rod!"
        boss = random.choice(FISH_BOSSES)
        if random.random() > (boss["risk"] - 0.15):
            u["wallet"] += boss["reward"]
            u["loot"][boss["drop"]] += 1
            response = f"🎣 Victory! Caught {boss['name']} for 🪙 {boss['reward']:,} & dropped {LOOT_ITEMS[boss['drop']]['name']}!"
        else:
            dead, death_msg = handle_death(u)
            response = f"💥 Dragged down by {boss['name']}! {death_msg}"

    elif cmd == "bank_heist":
        ok, msg = check_status(u)
        if not ok: return msg
        weights = [c["weight"] for c in BANK_CLERKS]
        clerk = random.choices(BANK_CLERKS, weights=weights, k=1)[0]
        if random.random() > clerk["risk"]:
            u["wallet"] += clerk["reward"]
            u["loot"][clerk["drop"]] += 1
            response = f"🎉 Bank Heist Success! Bypassed {clerk['name']} and stole 🪙 {clerk['reward']:,} & looted {LOOT_ITEMS[clerk['drop']]['name']}!"
        else:
            dead, death_msg = handle_death(u)
            response = f"🚨 Caught by {clerk['name']}! {death_msg}"

    elif cmd == "rob":
        ok, msg = check_status(u)
        if not ok: return msg
        if not args: return "❌ Usage: `rob <username>`"
        target_name = args[0]
        if target_name == username: return "❌ Can't rob yourself."
        if target_name not in room["players"]: return "❌ Player not found in room."
        target = room["players"][target_name]
        if target["dead"] or target["wallet"] < 200: return "❌ Target is dead or too poor."
        if target["inventory"]["golden_padlock"] > 0: return "🔒 Target's Golden Padlock blocked your robbery!"
        if target["inventory"]["padlock"] > 0:
            target["inventory"]["padlock"] -= 1
            return "🔒 Target's Padlock broke and stopped your robbery!"

        if random.random() < 0.45:
            steal_amt = int(target["wallet"] * random.uniform(0.2, 0.5))
            target["wallet"] -= steal_amt
            u["wallet"] += steal_amt
            response = f"🥷 ROBBERY SUCCESS! Stole 🪙 {steal_amt:,} from {target_name}!"
        else:
            fine = min(u["wallet"], 1000)
            u["wallet"] -= fine
            target["wallet"] += fine
            response = f"🚨 Caught robbing {target_name}! Fined 🪙 {fine:,} paid to victim."

    elif cmd == "donate":
        ok, msg = check_status(u)
        if not ok: return msg
        if len(args) < 2: return "❌ Usage: `donate <username> <amount>`"
        target_name = args[0]
        try: amt = int(args[1])
        except: return "❌ Invalid amount."
        if target_name not in room["players"] or amt <= 0 or amt > u["wallet"]:
            return "❌ Invalid target or wallet funds."
        u["wallet"] -= amt
        room["players"][target_name]["wallet"] += amt
        response = f"🎁 Donated 🪙 {amt:,} to {target_name}!"

    elif cmd == "revive":
        if len(args) < 1: return "❌ Usage: `revive <username>`"
        target_name = args[0]
        if target_name not in room["players"]: return "❌ Player not found."
        target = room["players"][target_name]
        if not target["dead"]: return f"❌ {target_name} is not dead."

        if u["inventory"]["reviver"] > 0:
            u["inventory"]["reviver"] -= 1
            target["dead"] = False
            target["wallet"] = 500
            response = f"✨ Resurrected {target_name} using Reviver Token!"
        elif u["wallet"] >= 1000000:
            u["wallet"] -= 1000000
            target["dead"] = False
            target["wallet"] = 500
            response = f"✨ Paid 1,000,000 Coins to resurrect {target_name}!"
        else:
            return "❌ Need a Reviver Token or 1,000,000 Coins in wallet to revive!"

    elif cmd == "sell":
        ok, msg = check_status(u)
        if not ok: return msg
        if not args: return "❌ Usage: `sell <item_id>` or `sell all`"
        if args[0].lower() == "all":
            earned = 0
            for k, v in u["loot"].items():
                if v > 0:
                    earned += v * LOOT_ITEMS[k]["sell_price"]
                    u["loot"][k] = 0
            u["wallet"] += earned
            response = f"💰 Sold all boss loot for 🪙 {earned:,}!"
        else:
            item = args[0].lower()
            if item not in LOOT_ITEMS or u["loot"][item] <= 0:
                return "❌ You don't own this loot item."
            qty = u["loot"][item]
            payout = qty * LOOT_ITEMS[item]["sell_price"]
            u["loot"][item] = 0
            u["wallet"] += payout
            response = f"💰 Sold {qty}x {LOOT_ITEMS[item]['name']} for 🪙 {payout:,}!"

    elif cmd in ["leaderboard", "lb"]:
        def calc_nw(p):
            inv_v = sum(p["inventory"][k] * SHOP_ITEMS[k]["price"] for k in p["inventory"])
            loot_v = sum(p["loot"][k] * LOOT_ITEMS[k]["sell_price"] for k in p["loot"])
            return p["wallet"] + p["bank"] + inv_v + loot_v
        ranked = sorted(room["players"].items(), key=lambda x: calc_nw(x[1]), reverse=True)
        response = "🏆 ROOM LEADERBOARD:\n" + "\n".join([f"{i}. **{p[0]}** — 🪙 {calc_nw(p[1]):,} Net Worth" for i, p in enumerate(ranked[:10], 1)])

    else:
        response = f"❌ Unknown command `{cmd}`. Type `help`."

    save_rooms(rooms)
    return response

@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Scam Jose Paul - Multiplayer League</title>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: monospace; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: #1e293b; padding: 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
        input, button { background: #334155; color: #fff; border: 1px solid #475569; padding: 10px; margin: 5px 0; border-radius: 4px; font-family: monospace; }
        button { cursor: pointer; background: #2563eb; font-weight: bold; }
        button:hover { background: #1d4ed8; }
        .game-layout { display: flex; gap: 15px; margin-top: 10px; }
        .main-pane { flex: 3; }
        .sidebar { flex: 1; background: #090d16; padding: 15px; border-radius: 4px; border: 1px solid #334155; max-height: 420px; overflow-y: auto; }
        #terminal { background: #090d16; padding: 15px; height: 350px; overflow-y: auto; border-radius: 4px; border: 1px solid #334155; white-space: pre-wrap; margin-bottom: 10px; }
        .flex { display: flex; gap: 10px; }
        .flex input { flex: 1; }
        ul { padding-left: 15px; margin: 5px 0; }
        li { color: #38bdf8; margin-bottom: 4px; }
    </style>
</head>
<body>
<div class="container">
    <h2>🎮 Scam Jose Paul - Multiplayer League</h2>
    <div id="setup-box">
        <h3>Create or Join Room</h3>
        <input type="text" id="username" placeholder="Enter Username"><br>
        <input type="text" id="roomcode" placeholder="Enter Room Code (e.g., JOSE99)"><br>
        <button onclick="createRoom()">Create Room (Host)</button>
        <button onclick="joinRoom()">Join Room</button>
    </div>
    <div id="game-box" style="display:none;">
        <h3 id="room-title"></h3>
        <div class="game-layout">
            <div class="main-pane">
                <div id="terminal">Connected to Scam Jose Paul League...\nType normal text to chat publicly, or type game commands (work, hunt, shop).\nType `/whisper <username> <message>` for secret chats.</div>
                <div class="flex">
                    <input type="text" id="command-input" placeholder="Type command or chat message..." onkeydown="if(event.key==='Enter') sendCommand()">
                    <button onclick="sendCommand()">Send</button>
                </div>
            </div>
            <div class="sidebar">
                <h4>🟢 Active Players</h4>
                <ul id="player-list"></ul>
            </div>
        </div>
        <button onclick="endRoom()" style="background:#dc2626; margin-top:15px; display:none;" id="host-btn">🛑 End League (Host Only)</button>
    </div>
</div>
<script>
    let ws, room, user;
    function createRoom() {
        user = document.getElementById('username').value.trim();
        room = document.getElementById('roomcode').value.trim().toUpperCase();
        if(!user || !room) return alert('Enter username and room code.');
        fetch('/api/create', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({room, host:user})})
        .then(r => r.json()).then(res => { if(res.error) alert(res.error); else connectWS(true); });
    }
    function joinRoom() {
        user = document.getElementById('username').value.trim();
        room = document.getElementById('roomcode').value.trim().toUpperCase();
        if(!user || !room) return alert('Enter username and room code.');
        connectWS(false);
    }
    function connectWS(isHost) {
        document.getElementById('setup-box').style.display = 'none';
        document.getElementById('game-box').style.display = 'block';
        document.getElementById('room-title').innerText = `Room: ${room} | Player: ${user}`;
        if(isHost) document.getElementById('host-btn').style.display = 'block';

        let proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        ws = new WebSocket(`${proto}//${window.location.host}/ws/${room}/${user}`);
        
        ws.onmessage = function(event) {
            let data = event.data;
            try {
                let parsed = JSON.parse(data);
                if(parsed.type === "players") {
                    let list = document.getElementById('player-list');
                    list.innerHTML = "";
                    parsed.players.forEach(p => {
                        let li = document.createElement('li');
                        li.innerText = p === user ? `${p} (You)` : p;
                        list.appendChild(li);
                    });
                    return;
                }
            } catch(e) {}

            let term = document.getElementById('terminal');
            term.innerText += `\\n> ${data}`;
            term.scrollTop = term.scrollHeight;
        };
    }
    function sendCommand() {
        let inp = document.getElementById('command-input');
        let val = inp.value.trim();
        if(!val) return;
        
        // Instantly echo command locally so you always see what you typed
        let term = document.getElementById('terminal');
        term.innerText += `\\n> [You]: ${val}`;
        term.scrollTop = term.scrollHeight;

        ws.send(val);
        inp.value = '';
    }
    function endRoom() {
        fetch('/api/end', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({room, host:user})})
        .then(() => { alert('League ended.'); location.reload(); });
    }
</script>
</body>
</html>
"""

@app.post("/api/create")
def create_room_api(data: dict):
    rooms = load_rooms()
    room = data["room"]
    host = data["host"]
    if room in rooms:
        return {"error": "Room code already exists."}
    rooms[room] = {"host": host, "active": True, "players": {}}
    save_rooms(rooms)
    return {"status": "ok"}

@app.post("/api/end")
def end_room_api(data: dict):
    rooms = load_rooms()
    room = data["room"]
    if room in rooms:
        rooms[room]["active"] = False
        save_rooms(rooms)
    for ws in connected_clients.get(room, {}).values():
        try: ws.close()
        except: pass
    return {"status": "ok"}

@app.websocket("/ws/{room_code}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_code: str, username: str):
    await websocket.accept()
    rooms = load_rooms()
    if room_code not in rooms:
        rooms[room_code] = {"host": username, "active": True, "players": {}}
    
    get_user_in_room(rooms[room_code], username)
    save_rooms(rooms)

    if room_code not in connected_clients:
        connected_clients[room_code] = {}
    connected_clients[room_code][username] = websocket

    if room_code in connected_clients:
        join_msg = f"🔔 {username} has entered the room!"
        for uname, ws in connected_clients[room_code].items():
            if uname != username:
                try: await ws.send_text(join_msg)
                except: pass

    await websocket.send_text(f"Welcome to Scam Jose Paul League [{room_code}]! Type `help` to start.")
    await broadcast_room_state(room_code)
    
    try:
        while True:
            data = await websocket.receive_text()
            res = await process_command(room_code, username, data)
            if res:
                await websocket.send_text(res)
    except WebSocketDisconnect:
        pass
    finally:
        if room_code in connected_clients and username in connected_clients[room_code]:
            del connected_clients[room_code][username]
        leave_msg = f"🚪 {username} has left the room."
        if room_code in connected_clients:
            for ws in connected_clients[room_code].values():
                try: await ws.send_text(leave_msg)
                except: pass
        await broadcast_room_state(room_code)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
