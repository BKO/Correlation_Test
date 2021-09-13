from mysql.connector import connect, Error, errorcode
from enum import Enum


class DbStatusCodes(Enum):
    DB_FOUND        = 0
    DB_NOT_FOUND    = 1
    OTHER_ERROR     = 2


def check_db(dbName):
    host = 'localhost'
    user = 'root'
    try:
        connection = connect(
            host=host,
            user=user,
            passwd='diggitydogdog',
            database=dbName
        )
        print('MySQL Connection Successful')
        connection.close()
        return DbStatusCodes.DB_FOUND
    except Error as err:
        print('Error in MySql Connection: {0}'.format(err))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database not found')
            return DbStatusCodes.DB_NOT_FOUND
        else:
            return DbStatusCodes.OTHER_ERROR


def getConnection(dbName):
    host = 'localhost'
    user = 'root'
    try:
        connection = connect(
            host='localhost',
            user='root',
            passwd='diggitydogdog',
            database=dbName
        )
        print('MySQL Connection Successful')
        return connection
    except Error as err:
        print('Error in MySql Connection: {0}'.format(err))


def make_db(dbName):
    try:
        connection = connect(
            host='localhost',
            user='root',
            passwd='diggitydogdog'
        )
    except Error as err:
        print('Error: {0}'.format(err))
        return False
    query = 'CREATE DATABASE {0}'.format(dbName)
    cursor = connection.cursor()
    cursor.execute(query)
    cursor.close()
    connection.close()
    print('Database successfully created')
    make_tables()


def make_user_table(connection):
    cursor = connection.cursor()
    user_create = '''
              CREATE table users (
                  session_id CHAR(32) PRIMARY KEY,
                  name VARCHAR(40) NOT NULL,
                  surname VARCHAR(40) NOT NULL,
                  email VARCHAR(40) NOT NULL
              );
          '''
    cursor.execute(user_create)
    cursor.close()


def make_question_table(connection):
    cursor = connection.cursor()
    question_create = '''
        CREATE table questions (
            question_id INT PRIMARY KEY,
            body TEXT NOT NULL
        );
    '''
    cursor.execute(question_create)

    insert_sql = 'INSERT INTO questions (question_id, body) VALUES (%s, %s)'
    insert_vals = [
        ('1', 'How are you?'),
        ('2', 'What is 1+1'),
        ('3', 'What did you have for dinner?'),
        ('4', 'What color is your shirt?'),
    ]
    cursor.executemany(insert_sql, insert_vals)

    answer_create = '''
        CREATE table answers (
            answer_id INT,
            question_id INT,
            answer_text TINYTEXT NOT NULL
        );
    '''
    cursor.execute(answer_create)

    answer_insert = 'INSERT INTO answers (answer_id, question_id, answer_text) VALUES (%s, %s, %s)'
    answer_vals = [
        ('1', '1', 'Not good'),
        ('2', '1', 'great'),
        ('3', '1', 'very good'),
        ('4', '1', 'definitely not good'),
        ('1', '2', '0'),
        ('2', '2', '1'),
        ('3', '2', '2'),
        ('4', '2', '-1'),
        ('1', '3', 'bread'),
        ('2', '3', 'steak'),
        ('3', '3', 'dinner'),
        ('4', '3', 'none of the above'),
        ('1', '4', 'red'),
        ('2', '4', 'white'),
        ('3', '4', 'blue'),
        ('4', '4', 'yellow'),
    ]

    cursor.executemany(answer_insert, answer_vals)

    cursor.close()


def make_assessment_status_table(connection):
    cursor = connection.cursor()
    user_create = '''
                 CREATE table assessment_status (
                     session_id CHAR(32) PRIMARY KEY,
                     question_1 TINYTEXT,
                     question_2 TINYTEXT,
                     question_3 TINYTEXT,
                     question_4 TINYTEXT,
                     start_time TINYTEXT
                 );
             '''
    cursor.execute(user_create)
    cursor.close()


def make_tables():
    connection = getConnection('john_interview_test')
    make_user_table(connection)
    make_question_table(connection)
    make_assessment_status_table(connection)

    connection.commit()
    connection.close()


def setup():
    print('Starting db setup')
    db_exists = check_db('john_interview_test')
    if db_exists == DbStatusCodes.DB_NOT_FOUND:
        if make_db('john_interview_test'):
            return True
        else:
            return False
    elif db_exists == DbStatusCodes.OTHER_ERROR:
        return False
    else:
        return True
