from database import Session
from database.models import User


async def is_user(id_user: int, session: Session = Session()) -> bool:
    user: User = session.query(User).filter(User.id == id_user).first()
    return True if user else False
