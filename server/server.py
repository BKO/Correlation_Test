from flask import Flask, jsonify, request
import secrets
from server.db import getConnection
import time


app = Flask(__name__)


def retrieve_question(question_id):
    db = getConnection('john_interview_test')
    cursor = db.cursor()
    query = '''
        SELECT body
        FROM questions
        WHERE question_id = '{0}'
        '''.format(question_id)
    cursor.execute(query)
    question = cursor.fetchall()[0]
    answer_query = '''
        SELECT answer_id, answer_text
        FROM answers 
        WHERE question_id = '{0}'
    '''.format(question_id)

    cursor.execute(answer_query)
    answers = cursor.fetchall()
    cursor.close()
    db.close()

    data = {}
    data['text'] = question[0]
    data['Id'] = question_id

    options = []
    for a in answers:
        options.append({"Id": a[0], "Text": a[1]})

    data['Options'] = options
    response = {
        'Message': 'Success',
        'Data': data
    }

    return jsonify(response)


def store_answer(session_id, question_id, answer_id):

    db = getConnection('john_interview_test')
    cursor = db.cursor()
    query = '''
        UPDATE assessment_status 
        SET question_{0} = '{1}'
        WHERE session_id = '{2}';
    '''.format(question_id, answer_id, session_id)

    cursor.execute(query)
    db.commit()
    cursor.close()
    db.close()


def find_session(session_id):
    db = getConnection('john_interview_test')
    cursor = db.cursor()
    query = '''
        SELECT session_id, start_time
        FROM assessment_status
        WHERE session_id = '{0}'
    '''.format(session_id)
    cursor.execute(query)
    matching_sessions = cursor.fetchall()
    cursor.close()
    db.close()

    if not matching_sessions:
        return None

    session = matching_sessions[0][0]
    start_time = float(matching_sessions[0][1])
    if time.time() - start_time >= 3600: # 3600 seconds = 1 hour
        return None
    else:
        return session


def store_session(name, surname, email):
    db = getConnection('john_interview_test')
    cursor = db.cursor()
    session = secrets.token_urlsafe(16)

    query = '''
        INSERT INTO users (session_id, name, surname, email)
        VALUES ('{0}', '{1}', '{2}', '{3}');
    '''.format(session, name, surname, email)
    cursor.execute(query)

    start_time = time.time()

    new_assessment_query = '''
        INSERT INTO assessment_status (session_id, start_time)
        VALUES('{0}', '{1}');
    '''.format(session, start_time)

    cursor.execute(new_assessment_query)

    db.commit()
    cursor.close()
    db.close()
    return session


def all_done(session_id):
    db = getConnection('john_interview_test')
    cursor = db.cursor()

    query = '''
        SELECT question_1, question_2, question_3, question_4
        FROM assessment_status
        WHERE session_id = '{0}';
    '''.format(session_id)
    cursor.execute(query)
    answers = cursor.fetchall()[0]

    cursor.close()
    db.close()
    return all(answers)


def send_timeout():
    response = {'Status': 0, 'Message': 'Failure, Timeout', 'Data': False}
    return jsonify(response)


@app.route('/test', methods=['GET'])
def test():
    return jsonify('test')


@app.route('/assessment/<session_id>/question/<question_id>', methods=['GET'])
def getQuestions(session_id, question_id):

    valid_session = find_session(session_id)
    if not valid_session:
        return send_timeout()
    else:
        return retrieve_question(question_id)


@app.route('/assessment/<session_id>/answer', methods=['POST'])
def answer(session_id):

    valid_session = find_session(session_id)

    if not valid_session:
        return send_timeout()

    question_id = request.form['QuestionId']
    answer_id = request.form['OptionId']

    store_answer(session_id, question_id, answer_id)

    if all_done(session_id):
        return jsonify({'Message': 'Complete', 'Data': False})

    return jsonify({'Message': 'Success', 'Data': True})


@app.route('/login', methods=['POST'])
def login():

    name = request.form['Name']
    surname = request.form['Surname']
    email = request.form['Email']

    session = store_session(name, surname, email)

    response = {'Message': 'Success', 'Data': session}
    return jsonify(response)


def run():
    print('starting flask')
    app_port = 8000
    app.run(host='0.0.0.0', port=app_port)


if __name__ == '__main__':
    print('running')

    port = 8000
    app.run(host='0.0.0.0', port=port)
