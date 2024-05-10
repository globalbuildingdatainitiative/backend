from uuid import UUID

from beanie import Document
from lcax import Project as LCAxProject


class DBProject(LCAxProject, Document):
    id: UUID
