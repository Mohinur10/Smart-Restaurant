# 🍽 Smart Restaurant QR System

Telegram orqali ishlaydigan to'liq restoran avtomatlashtirish tizimi: mijozlar QR kod orqali menyuni ko'rib buyurtma beradi, ofitsiant va oshxona real vaqtda xabar oladi, admin esa to'liq nazorat qiladi.

## 🚀 Texnologiyalar
- Python 3.11+
- aiogram 3 (Telegram Bot API)
- PostgreSQL + SQLAlchemy 2.0 (async)
- python-dotenv

## 📦 O'rnatish

1. Repozitoriyani yuklab oling va papkaga kiring:
```bash
cd smart_restaurant
```

2. Virtual muhit yarating va kutubxonalarni o'rnating:
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. `.env.example` faylidan `.env` yaratib, o'z ma'lumotlaringizni kiriting:
```bash
cp .env.example .env
```

`.env` ichida quyidagilarni to'ldiring:
- `BOT_TOKEN` — @BotFather'dan olingan token
- `DATABASE_URL` — PostgreSQL ulanish manzili (masalan: `postgresql+asyncpg://user:pass@localhost:5432/smart_restaurant`)
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` — bosh admin login/parol
- `SECRET_KEY` — parollarni hash qilish uchun maxfiy kalit

4. Botni ishga tushiring:
```bash
python -m app.bot
```

Birinchi marta ishga tushganda barcha jadvallar avtomatik yaratiladi va `.env`dagi login/parol bilan bosh admin akkaunti yaratiladi.

## 👤 Rollar va kirish

| Rol | Buyruq | Tavsif |
|---|---|---|
| Mijoz (User) | `/start` | QR kod orqali yoki to'g'ridan-to'g'ri kiradi |
| Admin | `/admin` | `.env` dagi login/parol bilan kiradi |
| Ofitsiant / Oshxona | `/staff` | Admin panel orqali yaratilgan login/parol bilan kiradi |

## 🪑 QR kod yaratish

1. Admin panelda **🪑 Stollar** bo'limiga kiring.
2. **➕ Yangi stol qo'shish** tugmasini bosing va stol raqamini kiriting.
3. Bot sizga noyob link beradi:
   `https://t.me/<bot_username>?start=table_<token>`
4. Shu linkdan istalgan QR generator (masalan, qr-code-generator.com) orqali QR rasm yarating va stol ustiga joylashtiring.

Mijoz QR kodni skaner qilganda bot avtomatik "Siz N-stoldasiz" deb tanitadi va shu stol raqami buyurtmaga bog'lanadi.

## 👥 Ofitsiant / Oshxona xodimini qo'shish

1. Admin panelda **👥 Xodimlar** → **🧑‍💼 Ofitsiant qo'shish** yoki **👨‍🍳 Oshpaz qo'shish**.
2. Ism, login va parol kiritiladi.
3. Xodim botga `/staff` buyrug'i bilan kirib, shu login/parol orqali tizimga kiradi.
4. Tizimga kirgandan so'ng, ularning Telegram ID'si avtomatik saqlanadi va yangi buyurtmalar haqida xabar olib turadi.

## 🛠 Asosiy funksiyalar

### Mijoz
- 📋 Menyu (kategoriyalar → mahsulotlar → tafsilotlar)
- 🛒 Savat (son o'zgartirish, izoh qo'shish, tozalash)
- 🍽 Shu yerda / 📦 Olib ketish, kishi soni, umumiy izoh
- 💳 To'lov turi (Naqd / Karta / Click / Payme)
- ❤️ Saqlangan mahsulotlar
- 🔍 Mahsulot qidirish (nomi, kodi, tarkibi bo'yicha)
- 📦 Buyurtmalar tarixi va ⭐ reyting berish
- 🎁 Bonus balans
- 📅 Stol band qilish (rezervatsiya)
- 🔔 Ofitsiant chaqirish

### Ofitsiant
- 📋 Faol buyurtmalarni ko'rish
- ✅ "Tayyor" bo'lgan buyurtmalarni "Yetkazildi" deb belgilash
- 🔔 Mijoz chaqirganda avtomatik xabar olish

### Oshxona
- 👨‍🍳 Navbatdagi buyurtmalar
- Holatni "Tayyorlanmoqda" → "Tayyor"ga o'zgartirish
- Tayyor bo'lganda mijoz va ofitsiantga avtomatik xabar

### Admin
- 📂 Kategoriyalar CRUD
- 📦 Mahsulotlar CRUD (rasm, narx, tavsif, tayyorlash vaqti, soni, kod)
- 🚚 Faol buyurtmalarni ko'rish
- 📊 Kunlik statistika (buyurtmalar soni, daromad, top mahsulot, band vaqt)
- 🎁 Promokod yaratish va boshqarish
- 👥 Xodimlarni (ofitsiant/oshxona) qo'shish, bloklash, o'chirish
- 🪑 Stollar va QR linklar

## 🖼 Rasmlar
Mahsulot rasmlari Telegram serverida `file_id` orqali saqlanadi — hech qanday tashqi (pullik) storage talab qilinmaydi.

## 🌐 Deploy (Render)

1. Render.com'da yangi **Background Worker** yarating.
2. Repozitoriyani ulang.
3. Build command: `pip install -r requirements.txt`
4. Start command: `python -m app.bot`
5. Environment Variables bo'limida `.env` dagi barcha o'zgaruvchilarni kiriting.
6. PostgreSQL bazasini Render'da yarating va `DATABASE_URL`ni ulang.

Bot **polling** rejimida ishlaydi — server qayta ishga tushganda avtomatik davom etadi, qo'shimcha webhook sozlash shart emas.

## 📁 Loyiha strukturasi

```
smart_restaurant/
├── app/
│   ├── bot.py            # Asosiy ishga tushirish fayli
│   ├── config.py         # .env sozlamalari
│   ├── database.py       # SQLAlchemy ulanish
│   ├── models/            # Database modellari
│   ├── handlers/
│   │   ├── user/          # Mijoz handlerlari
│   │   ├── admin/          # Admin panel handlerlari
│   │   ├── waiter/          # Ofitsiant handlerlari
│   │   └── kitchen/          # Oshxona handlerlari
│   ├── keyboards/          # Klaviaturalar
│   └── services/           # Biznes-logika (DB bilan ishlash)
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 🔒 Xavfsizlik
- Barcha maxfiy ma'lumotlar (`BOT_TOKEN`, `DATABASE_URL`, parollar, `SECRET_KEY`) `.env` faylida saqlanadi.
- `.env` fayli `.gitignore`ga qo'shilgan — hech qachon repozitoriyaga yuklanmaydi.
- Xodim parollari `PBKDF2-HMAC-SHA256` orqali hash qilinadi.
