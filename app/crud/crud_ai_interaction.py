from sqlalchemy.orm import Session
from app.models.ai_interaction import AIInteraction
from app.schemas.ai_interaction import AIInteractionCreate
from typing import Optional, List

class CRUDAIInteraction:
    def get_by_id(self, db: Session, interaction_id: int) -> Optional[AIInteraction]:
        return db.query(AIInteraction).filter(AIInteraction.id == interaction_id).first()
    
    def get_by_user_id(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[AIInteraction]:
        return db.query(AIInteraction).filter(AIInteraction.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_by_type(self, db: Session, interaction_type: str, skip: int = 0, limit: int = 100) -> List[AIInteraction]:
        return db.query(AIInteraction).filter(AIInteraction.interaction_type == interaction_type).offset(skip).limit(limit).all()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[AIInteraction]:
        return db.query(AIInteraction).offset(skip).limit(limit).all()
    
    def create(self, db: Session, interaction_data: AIInteractionCreate) -> AIInteraction:
        db_interaction = AIInteraction(**interaction_data.model_dump())
        db.add(db_interaction)
        db.commit()
        db.refresh(db_interaction)
        return db_interaction
    
    def delete(self, db: Session, interaction_id: int) -> bool:
        db_interaction = self.get_by_id(db, interaction_id)
        if db_interaction:
            db.delete(db_interaction)
            db.commit()
            return True
        return False

crud_ai_interaction = CRUDAIInteraction()