import enum
from sqlalchemy import Column, String, Float, Enum as SQLEnum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Operator(str, enum.Enum):
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="

class InvestmentPrinciple(Base):
    __tablename__ = "investment_principles"

    identifier = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    metric = Column(String, nullable=False)
    operator = Column(SQLEnum(Operator), nullable=False)
    threshold = Column(Float, nullable=False)
    description = Column(String, nullable=False)

