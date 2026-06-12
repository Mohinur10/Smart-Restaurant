"""FSM holatidagi staff_role asosida ruxsatlarni tekshiruvchi filterlar."""
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from aiogram.fsm.context import FSMContext


class _RoleFilter(BaseFilter):
    role: str = ""

    async def __call__(self, event: TelegramObject, state: FSMContext) -> bool:
        data = await state.get_data()
        return data.get("staff_role") == self.role


class IsAdmin(_RoleFilter):
    role = "admin"


class IsWaiter(_RoleFilter):
    role = "waiter"


class IsKitchen(_RoleFilter):
    role = "kitchen"
