from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

# Машина состояний для пошагового сбора данных
class RequestForm(StatesGroup):
    waiting_for_device_type = State()
    waiting_for_description = State()
    waiting_for_price = State()

@router.message(RequestForm.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    """Сохраняем описание и переходим к запросу бюджета"""
    await state.update_data(description=message.text)
    await message.answer("💰 Введите желаемый бюджет на ремонт (только цифры):")
    await state.set_state(RequestForm.waiting_for_price)

@router.message(RequestForm.waiting_for_price)
async def process_price(message: types.Message, state: FSMContext):
    """Валидация цены и финализация заявки"""
    try:
        price = int(message.text.replace(" ", "").strip())
        if price <= 0:
            await message.answer("❌ Цена должна быть больше нуля! Введите заново:")
            return
            
        user_data = await state.get_data()
        device_type = user_data.get('device_type')
        description = user_data.get('description')
        
        # Здесь логика сохранения в БД (через DatabaseManager)
        
        await message.answer(
            f"🎉 <b>Заявка успешно создана!</b>\n"
            f"Устройство: {device_type}\n"
            f"Проблема: {description}\n"
            f"Бюджет: {price} руб.\n\n"
            f"Мастер свяжется с вами в ближайшее время.",
            parse_mode="HTML"
        )
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Пожалуйста, отправьте только цифры (например: 5000):")
