import enum
import pandas as pd
from sqlalchemy import (
    Column,
    Date,
    Enum as SQLEnum,
    Float,
    Integer,
    String,
    create_engine,
    func,
    select,
    text,
)
from sqlalchemy.orm import Session, declarative_base

# 1) CONHECENDO OS DADOS
print("=== 1) CARREGANDO E CONHECENDO OS DADOS ===")

CSV_PATH = "salaries.csv"  

df = pd.read_csv(CSV_PATH)

print("\n--- Primeiras 5 linhas ---")
print(df.head())

print("\n--- Estrutura e tipos de dados ---")
print(df.info())

print(f"\nValores únicos de SEX: {df['SEX'].dropna().unique()}")
print(f"Valores únicos de DESIGNATION: {df['DESIGNATION'].dropna().unique()}")
print(f"Valores únicos de UNIT: {df['UNIT'].dropna().unique()}")

df["DOJ"] = pd.to_datetime(df["DOJ"]).dt.date
df["CURRENT DATE"] = pd.to_datetime(df["CURRENT DATE"]).dt.date


# 2) MODELANDO OS DADOS COM ORM (SQLAlchemy)
print("\n=== 2) MODELANDO AS CLASSES ENUM E A TABELA ORM ===")

Base = declarative_base()


class SexEnum(str, enum.Enum):
    F = "F"
    M = "M"


class DesignationEnum(str, enum.Enum):
    ANALYST = "Analyst"
    SENIOR_ANALYST = "Senior Analyst"
    ASSOCIATE = "Associate"
    MANAGER = "Manager"
    SENIOR_MANAGER = "Senior Manager"
    DIRECTOR = "Director"


class UnitEnum(str, enum.Enum):
    FINANCE = "Finance"
    WEB = "Web"
    IT = "IT"
    OPERATIONS = "Operations"
    MARKETING = "Marketing"
    MANAGEMENT = "Management"



class Funcionario(Base):
    __tablename__ = "salarios"

    
    id = Column(Integer, primary_key=True, autoincrement=True)

    
    first_name = Column("FIRST NAME", String, nullable=True)
    last_name = Column("LAST NAME", String, nullable=True)
    SEX = Column(
        "SEX",
        SQLEnum(SexEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    DOJ = Column("DOJ", Date, nullable=True)
    current_date = Column("CURRENT DATE", Date, nullable=True)
    DESIGNATION = Column(
        "DESIGNATION",
        SQLEnum(
            DesignationEnum, values_callable=lambda x: [e.value for e in x]
        ),
        nullable=True,
    )
    AGE = Column("AGE", Integer, nullable=True)
    SALARY = Column("SALARY", Float, nullable=True)
    UNIT = Column(
        "UNIT",
        SQLEnum(UnitEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    leaves_used = Column("LEAVES USED", Integer, nullable=True)
    leaves_remaining = Column("LEAVES REMAINING", Integer, nullable=True)
    RATINGS = Column("RATINGS", Float, nullable=True)
    past_exp = Column("PAST EXP", Float, nullable=True)


# 3) ESTABELECENDO UMA CONEXÃO
print("\n=== 3) CRIANDO A CONEXÃO COM O BANCO SQLite ===")
engine = create_engine("sqlite:///salarios.db", echo=False)
print("Engine criada com sucesso:", engine)



# 4) CRIANDO AS TABELAS
print("\n=== 4) CRIANDO AS TABELAS NO BANCO ===")
Base.metadata.create_all(engine)
print("Tabela 'salarios' criada com sucesso no banco de dados!")


# 5) POPULANDO O BANCO COM PANDAS
print("\n=== 5) POPULANDO O BANCO ===")
df.to_sql(name="salarios", con=engine, if_exists="append", index=False)
print(f"Foram inseridos {len(df)} registros com sucesso!")


# 6) CONSULTAS SQL VS ORM

print("\n=== 6) CONSULTAS: SQL vs ORM ===")

sql_query = text("""
    SELECT 
        "DESIGNATION",
        MIN("SALARY" / 12.0) AS min_salario_mensal,
        MAX("SALARY" / 12.0) AS max_salario_mensal,
        AVG("SALARY" / 12.0) AS media_salario_mensal
    FROM salarios
    WHERE "DESIGNATION" IS NOT NULL
    GROUP BY "DESIGNATION";
""")

print("\n--- Forma 1: Execução direta via engine.connect() ---")
with engine.connect() as conn:
    resultado = conn.execute(sql_query)
    for row in resultado:
        print(
            f"Cargo: {row[0]:<15} | Mín: {row[1]:>8.2f} | Máx: {row[2]:>8.2f} | Média: {row[3]:>8.2f}"
        )

print("\n--- Forma 2: Execução via pd.read_sql_query() ---")
with engine.connect() as conn:
    df_resultado = pd.read_sql_query(sql_query, con=conn)
    print(df_resultado.to_string(index=False))

print("\n--- Forma 3: Execução via ORM select() com Session(engine) ---")
stmt = (
    select(
        Funcionario.DESIGNATION,
        func.min(Funcionario.SALARY / 12.0).label("min_salario_mensal"),
        func.max(Funcionario.SALARY / 12.0).label("max_salario_mensal"),
        func.avg(Funcionario.SALARY / 12.0).label("media_salario_mensal"),
    )
    .where(Funcionario.DESIGNATION.is_not(None))
    .group_by(Funcionario.DESIGNATION)
)

with Session(engine) as session:
    resultado_orm = session.execute(stmt).all()
    for row in resultado_orm:
        print(
            f"Cargo: {row.DESIGNATION:<15} | Mín: {row.min_salario_mensal:>8.2f} | Máx: {row.max_salario_mensal:>8.2f} | Média: {row.media_salario_mensal:>8.2f}"
        )