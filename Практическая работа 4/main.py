from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="TicketBook Emulator")

# Временное хранилище в памяти для симуляции базы данных
db = {
    "valid_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_session_token",
    "active_bookings": {}  # booking_id: status
}

# --- МОДЕЛИ ДАННЫХ (Pydantic) ---
class LoginRequest(BaseModel):
    login: str
    pass_word: str  # В схеме pass, но в python 'pass' - зарезервированное слово

class BookingRequest(BaseModel):
    event_id: int

class PaymentRequest(BaseModel):
    booking_id: int
    card_token: str

# --- ВСПЕМОГАТЕЛЬНАЯ ФУНКЦИЯ ПРОВЕРКИ ТОКЕНА ---
def verify_token(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    token = authorization.split(" ")[1]
    if token != db["valid_token"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# --- РУТЫ СИСТЕМЫ TICKETBOOK ---

# TC-INT-01: Авторизация (M1 Auth)
@app.post("/api/auth/login")
def login(data: LoginRequest):
    if data.login == "user@test.com" and data.pass_word == "Test1234!":
        return {"session_token": db["valid_token"]}
    raise HTTPException(status_code=400, detail="Wrong credentials")

# TC-INT-01, TC-INT-02, TC-INT-03: Создание бронирования (M3 Booking)
@app.post("/api/booking/create")
def create_booking(data: BookingRequest, authorization: Optional[str] = Header(None)):
    # Проверка токена (TC-INT-02)
    verify_token(authorization)
    
    # Проверка существующего мероприятия (TC-INT-03)
    if data.event_id == 99999:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    # Успешный сценарий (TC-INT-01)
    # Генерируем фиксированный booking_id для простоты тестирования
    booking_id = 451
    db["active_bookings"][booking_id] = "pending"
    return {"booking_id": booking_id, "status": "pending"}

# TC-INT-04, TC-INT-05, TC-INT-06: Оплата (M4 Payment)
@app.post("/api/payment/pay")
def pay_booking(data: PaymentRequest):
    booking_id = data.booking_id
    
    # Проверяем, существует ли бронь
    if booking_id not in db["active_bookings"]:
        # Если это новая бронь для TC-INT-06, которой нет в базе, добавим её как pending
        db["active_bookings"][booking_id] = "pending"

    current_status = db["active_bookings"][booking_id]

    # TC-INT-05: Двойная оплата
    if current_status == "paid":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking already paid")
    
    # TC-INT-06: Отказ платежной системы
    if data.card_token == "tok_test_decline":
        db["active_bookings"][booking_id] = "failed"
        raise HTTPException(status_code=402, detail={"payment_status": "declined", "status": "failed"})
    
    # TC-INT-04: Успешная оплата
    if data.card_token == "tok_test_valid":
        db["active_bookings"][booking_id] = "paid"
        return {"payment_status": "success", "booking_id": booking_id}
    
    raise HTTPException(status_code=400, detail="Invalid card token")

# Проверка статуса брони (Используется для проверки в шагах TC-INT-04, TC-INT-06)
@app.get("/api/booking/{booking_id}")
def get_booking(booking_id: int):
    if booking_id not in db["active_bookings"]:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"booking_id": booking_id, "status": db["active_bookings"][booking_id]}