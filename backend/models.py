from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from database import Base, engine

# i create the tables in the database

# the user table
class User(Base):
    __tablename__ = "Users"
    id_user = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255),unique=True)
    password = Column(String(255)) # for now it's a string, but later it will be hashed
    ip_adress = Column(String(256))
    id_role = Column(Integer, ForeignKey("Roles.id_role"))
    id_files = Column(Integer, ForeignKey("Files.id_file"))

# the user_files table, made to manage the m-m relationship between users and files
class User_Files(Base):
    __tablename__ = "User_Files"
    id_user_files = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey("Users.id_user"))
    id_file = Column(Integer, ForeignKey("Files.id_file"))
    inSync = Column(Boolean, default=False) # bool to see if 2 files are in sync

# the files table, data about the files
class File(Base):
    __tablename__ = "Files"
    id_file = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), unique=True)
    id_type = Column(Integer, ForeignKey("Types.id_type"))
    file_path = Column(String(255), unique=True)
    file_size = Column(Integer)
    upload_time = Column(DateTime)

# the file types table, if i want to to filter the files
class Type(Base):
    __tablename__ = "Types"
    id_type = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(255), unique=True)

# the roles table: admin, storage, user
class Role(Base):
    __tablename__ = "Roles"
    id_role = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(255), unique=True)

print("I have created the tables :)")

Base.metadata.create_all(bind=engine) # create the tables in the database