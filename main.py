
from ai_service import generate_customer_response
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
from database import create_tables, get_connection

app = FastAPI(
    title="AI Customer Support System",
    description="Customer Support and Ticket Management API",
    version="1.0.0"
)

# Enable frontend-backend communication
app.add_middleware(
    CORSMiddleware,
 allow_origins=[
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://sunny-fudge-51ea0a.netlify.app"
],
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
create_tables()


# Ticket input validation
class TicketCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    email: str
    subject: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=10)


class TicketStatusUpdate(BaseModel):
    status: Literal["Open", "In Progress", "Resolved"]


# Automatic ticket category and priority classification
def classify_ticket(subject, description):
    message = (subject + " " + description).lower()

    # Category detection
    if any(word in message for word in ["login", "password", "account", "sign in"]):
        category = "Account Access"
    elif any(word in message for word in ["payment", "refund", "billing", "invoice"]):
        category = "Billing"
    elif any(word in message for word in ["error", "bug", "crash", "technical", "not working"]):
        category = "Technical Support"
    else:
        category = "General"

    # Priority detection
    if any(word in message for word in [
        "urgent", "critical", "security breach", "hacked",
        "unable", "cannot", "failed", "not working"
    ]):
        priority = "High"
    else:
        priority = "Medium"

    return category, priority


@app.get("/")
def home():
    return {
        "message": "Welcome to AI Customer Support System!",
        "status": "Running successfully"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Create customer support ticket
@app.post("/tickets", status_code=201)
def create_ticket(ticket: TicketCreate):
    connection = get_connection()

    try:
        category, priority = classify_ticket(
            ticket.subject,
            ticket.description
        )

        cursor = connection.execute(
            """
            INSERT INTO tickets
            (customer_name, email, subject, description, category, priority)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                ticket.customer_name,
                ticket.email,
                ticket.subject,
                ticket.description,
                category,
                priority
            )
        )

        connection.commit()
        ticket_id = cursor.lastrowid

        saved_ticket = connection.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()

        return dict(saved_ticket)

    except Exception as error:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not create ticket"
        ) from error

    finally:
        connection.close()


# Get all tickets
@app.get("/tickets")
def get_tickets():
    connection = get_connection()

    try:
        tickets = connection.execute(
            "SELECT * FROM tickets ORDER BY id DESC"
        ).fetchall()

        return [dict(ticket) for ticket in tickets]

    finally:
        connection.close()


# Update ticket status
@app.patch("/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id: int, update: TicketStatusUpdate):
    connection = get_connection()

    try:
        ticket = connection.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()

        if ticket is None:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found"
            )

        connection.execute(
            "UPDATE tickets SET status = ? WHERE id = ?",
            (update.status, ticket_id)
        )

        connection.commit()

        updated_ticket = connection.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()

        return dict(updated_ticket)

    finally:
        connection.close()


# Get individual ticket
@app.get("/tickets/{ticket_id}")
def get_ticket_by_id(ticket_id: int):
    connection = get_connection()

    try:
        ticket = connection.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()

        if ticket is None:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found"
            )

        return dict(ticket)

    finally:
        connection.close()


# Generate AI-suggested customer response
@app.post("/tickets/{ticket_id}/suggested-response")
def suggest_ticket_response(ticket_id: int):
    connection = get_connection()

    try:
        ticket = connection.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()

        if ticket is None:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found"
            )

        suggestion = generate_customer_response(
            ticket["subject"],
            ticket["description"],
            ticket["category"],
            ticket["priority"]
        )

        return {
            "ticket_id": ticket_id,
            "suggested_response": suggestion
        }

    finally:
        connection.close()
