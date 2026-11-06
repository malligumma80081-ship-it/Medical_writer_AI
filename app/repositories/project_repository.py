from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, project: Project):

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project

    def get_by_id(self, project_id):

        return self.db.get(Project, project_id)

    def get_by_owner(self, owner_id):

        statement = (
            select(Project)
            .where(Project.owner_id == owner_id)
            .order_by(Project.created_at.desc())
        )

        return list(self.db.scalars(statement).all())