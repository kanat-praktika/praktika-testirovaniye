from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="TicketBook Emulator")

db = {
    "valid_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_session_token",
    "active_bookings": {}
}

class LoginRequest(BaseModel):
    login: str
    pass_word: str

class BookingRequest(BaseModel):
    event_id: int

class PaymentRequest(BaseModel):
    booking_id: int
    card_token: str

def verify_token(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    token = authorization.split(" ")[1]
    if token != db["valid_token"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.post("/api/auth/login")
def login(data: LoginRequest):
    if data.login == "user@test.com" and data.pass_word == "Test1234!":
        return {"session_token": db["valid_token"]}
    raise HTTPException(status_code=400, detail="Wrong credentials")

@app.post("/api/booking/create")
def create_booking(data: BookingRequest, authorization: Optional[str] = Header(None)):
    verify_token(authorization)

    if data.event_id == 99999:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    booking_id = 451
    db["active_bookings"][booking_id] = "pending"
    return {"booking_id": booking_id, "status": "pending"}


@app.post("/api/payment/pay")
def pay_booking(data: PaymentRequest):
    booking_id = data.booking_id

    if booking_id not in db["active_bookings"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    current_status = db["active_bookings"][booking_id]

    if current_status == "paid":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking already paid")

    if data.card_token == "tok_test_decline":
        db["active_bookings"][booking_id] = "failed"
        raise HTTPException(status_code=402, detail={"payment_status": "declined", "status": "failed"})

    if data.card_token == "tok_test_valid":
        db["active_bookings"][booking_id] = "paid"
        return {"payment_status": "success", "booking_id": booking_id}
    
    raise HTTPException(status_code=400, detail="Invalid card token")

@app.get("/api/booking/{booking_id}")
def get_booking(booking_id: int):
    if booking_id not in db["active_bookings"]:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"booking_id": booking_id, "status": db["active_bookings"][booking_id]}