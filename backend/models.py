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
    media_id = Column(String, ForeignKey("media.id", ondelete="CASCADE"))
    start_ts = Column(Float)
    end_ts = Column(Float)
    mean_embedding = Column(Vector(512))

class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"
    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey("face_tracks.id", ondelete="CASCADE"))
    embedding = Column(Vector(512))

Index(
    "face_track_mean_ann_idx",
    FaceTrack.mean_embedding,
    postgresql_using="ivfflat",
    postgresql_with={"lists": 100}
)
