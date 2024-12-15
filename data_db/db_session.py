# Подключаем необходимы библиотеки
import sqlalchemy as sa
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

# Создадим две переменные: SqlAlchemyBase — некоторую абстрактную декларативную базу,
# в которую позднее будем наследовать все наши модели, и __factory, которую будем использовать для получения сессий
# подключения к нашей базе данных.
# Кроме того, в файле db_session.py нам понадобится сделать еще две функции global_init и create_session.
SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")
    # Подключаем базу данных
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
