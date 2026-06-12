"""Admin: Aksiya / Promokod boshqaruvi."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin_kb import admin_promo_main_kb, admin_promo_list_kb
from app.services.promo_service import create_promo, get_all_promos, toggle_promo, delete_promo
from app.utils.callbacks import AdminPromoCB
from app.utils.states import PromoForm
from app.utils.filters import IsAdmin

router = Router(name="admin_promo")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(F.text.in_({"🎁 Aksiya", "🎁 Aksiyalar"}))
async def promo_menu(message: Message) -> None:
    promos = await get_all_promos()
    if promos:
        await message.answer("🎁 <b>Mavjud promokodlar:</b>", reply_markup=admin_promo_list_kb(promos))
    await message.answer("Yangi promokod yaratish:", reply_markup=admin_promo_main_kb())


@router.callback_query(F.data == "aprm_new")
async def new_promo_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(PromoForm.waiting_code)
    await call.message.answer("🏷 Promokod nomini kiriting (masalan: SALOM10):")
    await call.answer()


@router.message(PromoForm.waiting_code)
async def new_promo_code(message: Message, state: FSMContext) -> None:
    await state.update_data(promo_code=message.text.strip().upper())
    await state.set_state(PromoForm.waiting_discount)
    await message.answer("📉 Chegirma foizini kiriting (masalan: 10):")


@router.message(PromoForm.waiting_discount)
async def new_promo_discount(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    if not text.isdigit() or not (0 < int(text) <= 100):
        await message.answer("⚠️ 1 dan 100 gacha raqam kiriting.")
        return
    await state.update_data(promo_discount=int(text))
    await state.set_state(PromoForm.waiting_limit)
    await message.answer("🔢 Necha marta ishlatilishi mumkin? (cheksiz uchun '-' yozing):")


@router.message(PromoForm.waiting_limit)
async def new_promo_limit(message: Message, state: FSMContext) -> None:
    text = message.text.strip()
    limit = int(text) if text.isdigit() else None

    data = await state.get_data()
    promo = await create_promo(code=data["promo_code"], discount_percent=data["promo_discount"], usage_limit=limit)
    await state.set_state(None)

    await message.answer(
        f"✅ Promokod yaratildi!\n\n🏷 Kod: <code>{promo.code}</code>\n📉 Chegirma: {promo.discount_percent}%"
    )

    promos = await get_all_promos()
    await message.answer("🎁 <b>Mavjud promokodlar:</b>", reply_markup=admin_promo_list_kb(promos))


@router.callback_query(AdminPromoCB.filter(F.action == "toggle"))
async def toggle_promo_handler(call: CallbackQuery, callback_data: AdminPromoCB) -> None:
    await toggle_promo(callback_data.id)
    promos = await get_all_promos()
    await call.message.edit_reply_markup(reply_markup=admin_promo_list_kb(promos))
    await call.answer("Holat o'zgartirildi")


@router.callback_query(AdminPromoCB.filter(F.action == "delete"))
async def delete_promo_handler(call: CallbackQuery, callback_data: AdminPromoCB) -> None:
    await delete_promo(callback_data.id)
    promos = await get_all_promos()
    await call.message.edit_reply_markup(reply_markup=admin_promo_list_kb(promos))
    await call.answer("O'chirildi")
