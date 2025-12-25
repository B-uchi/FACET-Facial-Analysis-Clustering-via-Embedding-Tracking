from sqlalchemy import (
    Column, String, Integer, Float, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Media(Base):
    __tablename__ = "media"
    id = Column(String, primary_key=True)
    filename = Column(String)

class FaceTrack(Base):
    __tablename__ = "face_tracks"
    id = Column(Integer, primary_key=True)
    media_id = Column(String, ForeignKey("media.id"))
    start_ts = Column(Float)
    end_ts = Column(Float)

class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"
    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey("face_tracks.id"))
    embedding = Column(Vector(512))

Index(
    "face_embedding_ann_idx",
    FaceEmbedding.embedding,
    postgresql_using="ivfflat",
    postgresql_with={"lists": 100}
)
