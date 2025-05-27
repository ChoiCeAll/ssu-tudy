from flask import Flask, request, jsonify, session, render_template, abort, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
import time
import traceback

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173", manage_session=False)

app.secret_key = 'your_secret_key'

# MySQL 설정
#app.config['MYSQL_HOST'] = 'mysql'
app.config['MYSQL_HOST'] = 'localhost'  # 또는 '127.0.0.1'

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'study'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


# 아이디 중복 확인
@app.route('/api/check-id', methods=['POST'])
def check_id():
    data = request.get_json()
    login_id = data.get('login_id')

    if not login_id:
        return jsonify({'error': '아이디를 입력하세요.'}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM User WHERE login_id = %s", (login_id,))
    exists = cur.fetchone()
    cur.close()

    return jsonify({'exists': bool(exists)})

# 회원가입
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json() if request.is_json else request.form
        login_id = data['login_id']
        password = data['password']
        id_checked = data.get('id_checked', True)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM User WHERE login_id = %s", (login_id,))
        if cur.fetchone():
            cur.close()
            return jsonify({'error': '이미 등록된 아이디입니다.'}), 400

        # 비밀번호 해시
        hashed_pw = generate_password_hash(password)
        cur.execute("INSERT INTO User (login_id, password) VALUES (%s, %s)", (login_id, hashed_pw))
        user_id = cur.lastrowid

        # ✅ 해시태그 정규화 처리
        raw_hashtags = data.get('hashtags', '')
        tags = [tag.strip().lstrip('#').lower() for tag in raw_hashtags.split(',') if tag.strip()]
        normalized_hashtags = ','.join(tags) if tags else None

        # MyPage 삽입
        name = data.get('name') or '슝슝이25'
        major = data.get('major') or 'AI융합학과'
        student_id = data.get('student_id') or '20252025'

        cur.execute("""
            INSERT INTO MyPage (user_id, name, major, student_id, hashtags)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            name,
            major,
            student_id,
            normalized_hashtags
        ))

        mysql.connection.commit()
        cur.close()
        return jsonify({'message': '회원가입 성공!'})
    except Exception as e:
        return jsonify({'error': '회원가입 실패', 'detail': str(e)}), 500


#비밀번호 재설정
@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    try:
        data = request.get_json() if request.is_json else request.form
        login_id = data['login_id']
        student_id = data['student_id']
        new_password = data['new_password']

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT u.user_id, u.password
            FROM User u
            JOIN MyPage m ON u.user_id = m.user_id
            WHERE u.login_id = %s AND m.student_id = %s
        """, (login_id, student_id))
        user = cur.fetchone()

        if not user:
            cur.close()
            return jsonify({'error': '아이디 또는 학번이 일치하지 않습니다.'}), 400

        if check_password_hash(user['password'], new_password):
            cur.close()
            return jsonify({'error': '이미 사용 중인 비밀번호입니다. 다른 비밀번호를 입력해주세요.'}), 400

        hashed_pw = generate_password_hash(new_password)
        cur.execute("UPDATE User SET password = %s WHERE login_id = %s", (hashed_pw, login_id))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': '비밀번호가 성공적으로 변경되었습니다.'}), 200

    except Exception as e:
        return jsonify({'error': '서버 오류', 'detail': str(e)}), 500




# 로그인
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json() if request.is_json else request.form
        login_id = data['login_id']
        password = data['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM User WHERE login_id = %s", [login_id])
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['login_id'] = user['login_id']

            # ✅ JSON 응답 추가
            return jsonify({
                'message': '로그인 성공',
                'user_id': user['user_id'],
                'login_id': user['login_id']
            }), 200
        else:
            return jsonify({'error': '아이디 또는 비밀번호가 잘못되었습니다.'}), 401
    except Exception as e:
        return jsonify({'error': '서버 오류', 'detail': str(e)}), 500

# 로그아웃
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('login_id', None)
    return jsonify({'message': '로그아웃 완료'}), 200


# 마이페이지 정보 조회
@app.route('/api/mypage/<int:user_id>', methods=['GET'])
def get_mypage(user_id):
    if not session.get('user_id') or session['user_id'] != user_id:
        return abort(403)

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM MyPage WHERE user_id = %s", [user_id])
    result = cur.fetchone()
    cur.close()

    if result:
        return jsonify(result)
    else:
        return jsonify({'error': '사용자 정보 없음'}), 404

#세션체크(새로고침 체크)
@app.route('/api/session-check', methods=['GET'])
def session_check():
    user_id = session.get('user_id')
    login_id = session.get('login_id')
    if user_id and login_id:
        return jsonify({
            'is_logged_in': True,
            'user_id': user_id,
            'login_id': login_id
        })
    else:
        return jsonify({'is_logged_in': False})


@app.route('/api/mypage/<int:user_id>/joined-studies')
def get_joined_studies(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return abort(403)
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT s.title, s.description 
        FROM Study s
        JOIN StudyMember sm ON s.study_id = sm.study_id
        WHERE sm.user_id = %s AND sm.is_approved = 1 AND s.is_active = TRUE
    """, [user_id])
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)

@app.route('/api/mypage/<int:user_id>/interested-studies')
def get_interested_studies(user_id):
    if not session.get('user_id') or session['user_id'] != user_id:
        return abort(403)

    cur = mysql.connection.cursor()
    # 유저가 설정한 해시태그 불러오기
    cur.execute("SELECT hashtags FROM MyPage WHERE user_id = %s", [user_id])
    row = cur.fetchone()

    if not row or not row['hashtags']:
        cur.close()
        return jsonify([])

    # 해시태그 여러 개 처리
    hashtags = [tag.strip() for tag in row['hashtags'].split(',') if tag.strip()]
    if not hashtags:
        cur.close()
        return jsonify([])

    # 조건 구성
    conditions = " OR ".join(["s.hashtags LIKE %s" for _ in hashtags])
    params = [f"%{tag}%" for tag in hashtags]

    # 관심 해시태그 매치 + 자신이 만든 스터디 제외 + 이미 참여한 스터디 제외
    cur.execute(f"""
        SELECT s.study_id, s.title, s.description, s.hashtags 
        FROM Study s
        WHERE s.is_active = TRUE
          AND ({conditions})
          AND s.leader_id != %s
          AND s.study_id NOT IN (
              SELECT sm.study_id FROM StudyMember sm
              WHERE sm.user_id = %s AND sm.is_approved = 1
          )
    """, params + [user_id, user_id])

    result = cur.fetchall()
    cur.close()
    return jsonify(result)


@app.route('/api/mypage/<int:user_id>/created-studies')
def get_created_studies(user_id):
    if not session.get('user_id') or session['user_id'] != user_id:
        return abort(403)

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT study_id, title, description, hashtags
        FROM Study
        WHERE leader_id = %s AND is_active = TRUE
    """, (user_id,))
    studies = cur.fetchall()
    cur.close()
    return jsonify(studies)

# 마이페이지 정보 수정
@app.route('/api/mypage/<int:user_id>', methods=['PUT'])
def update_mypage(user_id):
    if not session.get('user_id') or session['user_id'] != user_id:
        return abort(403)

    try:
        data = request.get_json()
        name = data.get('name', '')
        major = data.get('major', '')
        student_id = data.get('student_id', '')

        # ✅ 해시태그 정규화 처리
        raw_hashtags = data.get('hashtags', '')
        tags = [tag.strip().lstrip('#').lower() for tag in raw_hashtags.split(',') if tag.strip()]
        normalized_hashtags = ','.join(tags) if tags else None

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE MyPage
            SET name = %s, major = %s, student_id = %s, hashtags = %s
            WHERE user_id = %s
        """, (name, major, student_id, normalized_hashtags, user_id))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': '내정보 수정 완료'})
    except Exception as e:
        return jsonify({'error': '내정보 수정 실패', 'detail': str(e)}), 500


#스터디 목록 조회
@app.route('/api/studies', methods=['GET'])
def api_study_list():
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401

    keyword = request.args.get('keyword', '').strip()
    cur = mysql.connection.cursor()

    query = """
        SELECT s.study_id AS id, s.title AS name, s.hashtags,
               u.login_id AS leaderId, s.max_members AS capacity,
               s.time, s.image_base64
        FROM Study s
        JOIN User u ON s.leader_id = u.user_id
        WHERE s.is_active = TRUE
    """
    params = []

    if keyword:
        query += " AND (s.title LIKE %s OR s.hashtags LIKE %s)"
        search_term = f"%{keyword}%"
        params.extend([search_term, search_term])

    query += " ORDER BY s.created_at DESC"
    cur.execute(query, params)
    studies = cur.fetchall()

    for study in studies:
        study['description'] = '#' + study['hashtags'].replace(',', ' #') if study.get('hashtags') else ''
        study['members'] = 0

        # image_base64가 있으면 image로 설정, 없으면 None
        if study.get('image_base64'):
            study['image'] = study['image_base64']
        else:
            study['image'] = None

    cur.close()
    return jsonify(studies)




# 스터디 상세보기
@app.route('/api/studies/<int:study_id>', methods=['GET'])
def api_study_detail(study_id):
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT s.study_id AS id, s.title AS name, s.description,
               s.leader_id AS leaderId, u.login_id AS leaderLoginId,
               s.max_members AS capacity, s.time, s.hashtags, s.image_base64 AS image
        FROM Study s
        JOIN User u ON s.leader_id = u.user_id
        WHERE s.study_id = %s AND s.is_active = TRUE
    """, [study_id])

    study = cur.fetchone()
    if not study:
        cur.close()
        return jsonify({'error': '스터디 없음'}), 404

    # 참여 여부
    cur.execute("SELECT * FROM StudyMember WHERE study_id = %s AND user_id = %s", (study_id, user_id))
    study['is_applied'] = cur.fetchone() is not None

    study['members'] = 0
    if not study.get('image'):
        study['image'] = ''

    # 관심 등록 여부 확인 
    cur.execute("SELECT * FROM StudyMember WHERE study_id = %s AND user_id = %s AND is_approved IS NULL", (study_id, user_id))
    study['is_favorited'] = cur.fetchone() is not None

    cur.close()
    return jsonify(study)

# 관심 스터디 등록
@app.route('/api/study/<int:study_id>/favorite', methods=['POST'])
def mark_interest_study(study_id):
    if 'user_id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    try:
        cur.execute("""
            SELECT * FROM StudyMember 
            WHERE study_id = %s AND user_id = %s
        """, (study_id, user_id))
        existing = cur.fetchone()

        if not existing:
            cur.execute("""
                INSERT INTO StudyMember (study_id, user_id, is_approved)
                VALUES (%s, %s, NULL)
            """, (study_id, user_id))
            mysql.connection.commit()

        return jsonify({'message': '관심 스터디로 등록되었습니다.'}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': '관심 등록 실패', 'detail': str(e)}), 500
    finally:
        cur.close()


# 관심 스터디 해제
@app.route('/api/study/<int:study_id>/unfavorite', methods=['POST'])
def unmark_interest_study(study_id):
    if 'user_id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    try:
        cur.execute("""
            DELETE FROM StudyMember
            WHERE study_id = %s AND user_id = %s AND is_approved IS NULL
        """, (study_id, user_id))
        mysql.connection.commit()
        return jsonify({'message': '관심 스터디에서 해제되었습니다.'}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': '관심 해제 실패', 'detail': str(e)}), 500
    finally:
        cur.close()


#마이페이지에서 관심 등록 스터디 목록
@app.route('/api/mypage/<int:user_id>/favorited-studies')
def get_favorited_studies(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return abort(403)

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT s.study_id, s.title, s.description, s.hashtags
        FROM StudyMember sm
        JOIN Study s ON sm.study_id = s.study_id
        WHERE sm.user_id = %s AND sm.is_approved IS NULL AND s.is_active = TRUE
    """, (user_id,))
    favorites = cur.fetchall()
    cur.close()

    return jsonify(favorites)

# 스터디 생성
@app.route('/api/studies', methods=['POST'])
def api_study_create():
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401

    try:
        data = request.get_json()
        title = data.get('name')
        description = data.get('description')
        raw_tags = data.get('hashtags', '')
        max_members = data.get('capacity')
        time = data.get('time', '')
        image_base64 = data.get('image', '')
        leader_id = session['user_id']

        tags = [tag.strip().lstrip('#').lower() for tag in raw_tags.split(',') if tag.strip()]
        normalized_hashtags = ','.join(tags)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Study (title, description, leader_id, hashtags, max_members, created_at, is_active, time, image_base64)
            VALUES (%s, %s, %s, %s, %s, NOW(), TRUE, %s, %s)
        """, (title, description, leader_id, normalized_hashtags, max_members, time, image_base64))
        study_id = cur.lastrowid

        # ✅ 수정된 부분
        cur.execute("""
            INSERT INTO UserRoomStatus (user_id, study_id, in_room, first_messageSequence)
            VALUES (%s, %s, %s, %s)
        """, (leader_id, study_id, 1, 0))

        mysql.connection.commit()
        cur.close()

        return jsonify({'message': '스터디 등록 완료', 'id': study_id}), 201

    except Exception as e:
        traceback.print_exc()  # 전체 에러 스택 트레이스 출력
        return jsonify({'error': '스터디 등록 실패', 'detail': str(e)}), 500
    except Exception as e:
        return jsonify({'error': '스터디 등록 실패', 'detail': str(e)}), 500




# 스터디 수정
@app.route('/api/studies/<int:study_id>', methods=['PUT'])
def api_study_edit(study_id):
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401

    try:
        data = request.get_json()
        title = data.get('name')
        description = data.get('description')
        raw_tags = data.get('hashtags', '')
        max_members = data.get('capacity')
        time = data.get('time')
        image_base64 = data.get('image', '')  # ✅ base64 문자열

        tags = [tag.strip().lstrip('#').lower() for tag in raw_tags.split(',') if tag.strip()]
        normalized_hashtags = ','.join(tags)

        cur = mysql.connection.cursor()
        cur.execute("SELECT leader_id FROM Study WHERE study_id = %s", [study_id])
        study = cur.fetchone()

        if not study or study['leader_id'] != session['user_id']:
            cur.close()
            return jsonify({'error': '수정 권한 없음'}), 403

        cur.execute("""
            UPDATE Study
            SET title = %s, description = %s, hashtags = %s,
                max_members = %s, time = %s, image_base64 = %s
            WHERE study_id = %s
        """, (title, description, normalized_hashtags, max_members, time, image_base64, study_id))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': '스터디 수정 완료'})

    except Exception as e:
        return jsonify({'error': '수정 실패', 'detail': str(e)}), 500




#스터디 삭제
@app.route('/api/studies/<int:study_id>', methods=['DELETE'])
def api_delete_study(study_id):
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401

    cur = mysql.connection.cursor()
    cur.execute("SELECT leader_id FROM Study WHERE study_id = %s", (study_id,))
    study = cur.fetchone()

    if not study or study['leader_id'] != session['user_id']:
        cur.close()
        return jsonify({'error': '삭제 권한 없음'}), 403

    try:
        cur.execute("UPDATE Study SET is_active = FALSE WHERE study_id = %s", (study_id,))
        mysql.connection.commit()
        return jsonify({'message': '스터디 삭제 완료'})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': '삭제 실패', 'detail': str(e)}), 500
    finally:
        cur.close()


#댓글목록
@app.route('/api/comments', methods=['GET'])
def api_get_comments():
    study_id = request.args.get('study_id', type=int)
    if not study_id:
        return jsonify({'error': 'study_id가 필요합니다'}), 400

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.comment_id AS id, c.study_id, c.author_id,
        u.login_id AS author, c.content, c.created_at,
        c.parent_id
        
        FROM Comment c
        JOIN User u ON c.author_id = u.user_id
        WHERE c.study_id = %s AND c.is_active = TRUE
        ORDER BY c.created_at ASC
    """, (study_id,))
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)


# ✅ 댓글 추가
@app.route('/api/comments', methods=['POST'])
def api_add_comment():
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401

    data = request.get_json()
    study_id = data.get('study_id')
    content = data.get('content', '').strip()

    if not study_id or not content:
        return jsonify({'error': '유효하지 않은 요청'}), 400

    author_id = session['user_id']
    cur = mysql.connection.cursor()
    try:
        parent_id = data.get('parent_id')  #parent_id 받기
        cur.execute("""
            INSERT INTO Comment (study_id, author_id, content, parent_id, is_active)
            VALUES (%s, %s, %s, %s, TRUE)
        """, (study_id, author_id, content, parent_id))  

        comment_id = cur.lastrowid
        mysql.connection.commit()
        cur.execute("""
            SELECT c.comment_id AS id, c.content, c.created_at,
                c.author_id, u.login_id AS author,
                c.parent_id
            FROM Comment c JOIN User u ON c.author_id = u.user_id
            WHERE c.comment_id = %s
        """, (comment_id,))

        new_comment = cur.fetchone()
        return jsonify(new_comment), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': '댓글 등록 실패', 'detail': str(e)}), 500
    finally:
        cur.close()


# ✅ 댓글 수정
@app.route('/api/comments/<int:comment_id>', methods=['PUT'])
def api_edit_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401

    data = request.get_json()
    new_content = data.get('content', '').strip()

    if not new_content:
        return jsonify({'error': '내용이 비어있습니다'}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT author_id FROM Comment WHERE comment_id = %s AND is_active = TRUE", (comment_id,))
    comment = cur.fetchone()

    if not comment or comment['author_id'] != session['user_id']:
        cur.close()
        return jsonify({'error': '수정 권한이 없습니다'}), 403

    try:
        cur.execute("UPDATE Comment SET content = %s WHERE comment_id = %s", (new_content, comment_id))
        mysql.connection.commit()
        return jsonify({'message': '댓글 수정 완료'}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': 'DB 오류', 'detail': str(e)}), 500
    finally:
        cur.close()


# ✅ 댓글 삭제
@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def api_delete_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401

    cur = mysql.connection.cursor()
    cur.execute("SELECT author_id FROM Comment WHERE comment_id = %s AND is_active = TRUE", (comment_id,))
    comment = cur.fetchone()

    if not comment or comment['author_id'] != session['user_id']:
        cur.close()
        return jsonify({'error': '삭제 권한이 없습니다'}), 403

    try:
        cur.execute("UPDATE Comment SET is_active = FALSE WHERE comment_id = %s", (comment_id,))
        mysql.connection.commit()
        return jsonify({'message': '댓글 삭제 완료'}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': '댓글 삭제 실패', 'detail': str(e)}), 500
    finally:
        cur.close()



# ================= 알림 =================

@app.route('/api/notifications/<int:user_id>')
def get_notifications(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return abort(403)

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT notification_id, user_id, study_id, study_member_id, message, is_read, created_at
        FROM Notification
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, [user_id])
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)

@app.route('/notifications/read/<int:notification_id>', methods=['PUT'])
def mark_as_read(notification_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE Notification SET is_read = TRUE WHERE notification_id = %s", [notification_id])
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': '읽음 처리 완료'})

@app.route('/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    if 'user_id' not in session:
        return abort(403)
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id FROM Notification WHERE notification_id = %s", [notification_id])
    result = cur.fetchone()
    if not result or result['user_id'] != session['user_id']:
        cur.close()
        return abort(403)
    cur.execute("DELETE FROM Notification WHERE notification_id = %s", [notification_id])
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': '삭제 완료'})

@app.route('/notifications/<int:notification_id>/study')
def go_to_study_from_notification(notification_id):
    if 'user_id' not in session:
        return abort(403)
    cur = mysql.connection.cursor()
    cur.execute("SELECT study_id FROM Notification WHERE notification_id = %s AND user_id = %s", (notification_id, session['user_id']))
    row = cur.fetchone()
    cur.close()
    if not row or not row['study_id']:
        return jsonify({'error': '해당 알림에 연결된 스터디가 없습니다.'}), 404
    return redirect(f"/studies/{row['study_id']}")

# ================= 스터디 신청 / 승인 =================
@app.route('/api/study/<int:study_id>/apply', methods=['POST'])
def api_apply_to_study(study_id):
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # 이미 신청했는지 확인
    cur.execute("SELECT * FROM StudyMember WHERE study_id = %s AND user_id = %s", (study_id, user_id))
    if cur.fetchone():
        cur.close()
        return jsonify({'error': '이미 신청한 스터디입니다.'}), 400

    # 신청 insert
    cur.execute("INSERT INTO StudyMember (study_id, user_id, is_approved) VALUES (%s, %s, 0)", (study_id, user_id))
    study_member_id = cur.lastrowid

    # 스터디 정보 가져오기
    cur.execute("SELECT leader_id, title FROM Study WHERE study_id = %s", [study_id])
    study = cur.fetchone()

    if study:
        leader_id = study['leader_id']
        title = study['title']

        cur.execute("SELECT name, major FROM MyPage WHERE user_id = %s", [user_id])
        info = cur.fetchone()
        name, major = info['name'], info['major']

        message = f"[{title}] {name} ({major}) 님의 참여 신청이 도착했습니다."
        cur.execute("""
            INSERT INTO Notification (user_id, message, study_id, study_member_id, is_read, created_at)
            VALUES (%s, %s, %s, %s, FALSE, NOW())
        """, (leader_id, message, study_id, study_member_id))

    mysql.connection.commit()
    cur.close()
    return jsonify({'message': '스터디 신청이 완료되었습니다!'})

@app.route('/api/study/application/<int:study_member_id>', methods=['PUT'])
def decide_application(study_member_id):
    if 'user_id' not in session:
        return abort(403)

    decision = request.get_json().get('decision')
    if decision not in ['approve', 'reject']:
        return jsonify({'error': 'invalid decision'}), 400

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT sm.user_id, sm.study_id, s.leader_id, s.title
        FROM StudyMember sm
        JOIN Study s ON sm.study_id = s.study_id
        WHERE sm.study_member_id = %s
    """, [study_member_id])
    result = cur.fetchone()

    if not result or result['leader_id'] != session['user_id']:
        cur.close()
        return abort(403)

    applicant_id = result['user_id']
    study_id = result['study_id']
    study_title = result['title']

    if decision == 'approve':
        cur.execute("UPDATE StudyMember SET is_approved = 1 WHERE study_member_id = %s", [study_member_id])
        msg = f"[{study_title}] 스터디 신청이 승인되었습니다!"
        cur.execute("SELECT COALESCE(MAX(messageSequence), 0) + 1 AS seq FROM Chat WHERE study_id = %s", (study_id,))
        next_seq = cur.fetchone()['seq']
        cur.execute("""
            INSERT INTO UserRoomStatus (user_id, study_id, in_room, first_messageSequence)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE in_room = VALUES(in_room), first_messageSequence = VALUES(first_messageSequence)
        """, (applicant_id, study_id, 1, next_seq))
    else:
        cur.execute("DELETE FROM StudyMember WHERE study_member_id = %s", [study_member_id])
        msg = f"[{study_title}] 스터디 신청이 거절되었습니다."

    mysql.connection.commit()
    cur.close()
    return jsonify({'message': msg}), 200


# 채팅방 조회
@app.route('/api/mypage/<int:user_id>/chatrooms', methods=['GET'])
def get_my_chatrooms(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return abort(403)

    cur = mysql.connection.cursor()
    # 1) 먼저 방 목록을 가져오고
    cur.execute("""
        SELECT s.study_id, s.title, s.description, s.hashtags, s.time, s.created_at
        FROM UserRoomStatus urs
        JOIN Study s ON urs.study_id = s.study_id
        WHERE urs.user_id = %s AND urs.in_room = 1 AND s.is_active = TRUE
        ORDER BY s.created_at DESC
    """, (user_id,))
    rooms = cur.fetchall()

    # 2) 각 방마다 멤버 목록을 추가 조회해서 붙인다
    for room in rooms:
        cur.execute("""
            SELECT u.user_id,
                   m.name   AS nickname,
                   m.student_id,
                   m.major
            FROM UserRoomStatus urs
            JOIN User u ON urs.user_id = u.user_id
            LEFT JOIN MyPage m ON u.user_id = m.user_id
            WHERE urs.study_id = %s
              AND urs.in_room = 1
        """, (room['study_id'],))
        room['members'] = cur.fetchall()

    cur.close()
    return jsonify(rooms)




@app.route('/api/chatroom/<int:study_id>/members', methods=['GET'])
def get_chatroom_members(study_id):
    try:
        if 'user_id' not in session:
            return jsonify({'error': '로그인 필요'}), 401

        user_id = session['user_id']
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT 1 FROM UserRoomStatus
            WHERE user_id = %s AND study_id = %s
        """, (user_id, study_id))
        if not cur.fetchone():
            cur.close()
            return jsonify({'error': '접근 권한 없음'}), 403

        # LEFT JOIN 으로 수정
        cur.execute("""
            SELECT u.user_id, m.name AS nickname,
                   m.student_id, m.major
            FROM UserRoomStatus urs
            JOIN User u ON urs.user_id = u.user_id
            LEFT JOIN MyPage m ON u.user_id = m.user_id
            WHERE urs.study_id = %s
              AND urs.in_room = 1
        """, (study_id,))
        rows = cur.fetchall()
        cur.close()
        return jsonify(rows)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': '서버 내부 오류', 'details': str(e)}), 500




# ================= 채팅 =================
@app.route('/chat/<int:study_id>')
def chat(study_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', study_id=study_id)

@socketio.on('join')
def handle_join(data):
    room = data['study_id']
    user_id = session['user_id']
    login_id = session['login_id']
    join_room(room)

    cur = mysql.connection.cursor()

    # 기존에 join 기록이 있으면 그대로 사용
    cur.execute("""
        SELECT first_messageSequence FROM UserRoomStatus 
        WHERE user_id = %s AND study_id = %s
    """, (user_id, room))
    row = cur.fetchone()

    if row:
        first_messageSequence = row['first_messageSequence']
    else:
        # 없으면 처음부터 (0)로 시작
        first_messageSequence = 0
        cur.execute("""
            INSERT INTO UserRoomStatus (user_id, study_id, first_messageSequence)
            VALUES (%s, %s, %s)
        """, (user_id, room, first_messageSequence))
        mysql.connection.commit()

    # 이전 메시지 가져오기
    cur.execute("""
        SELECT c.user_id, u.login_id, c.message, c.messageSequence
        FROM Chat c JOIN User u ON c.user_id = u.user_id
        WHERE c.study_id = %s AND c.messageSequence >= %s
        ORDER BY c.messageSequence ASC
    """, (room, first_messageSequence))
    cur.execute("""
        SELECT c.user_id,
               u.login_id,
               c.message,
               c.messageSequence,
               c.created_at
        FROM Chat c
        JOIN User u ON c.user_id = u.user_id
        WHERE c.study_id = %s
          AND c.messageSequence >= %s
        ORDER BY c.messageSequence ASC
    """, (room, first_messageSequence))
    messages = cur.fetchall()
    cur.close()

    for msg in messages:
        emit('message', {
            'user_id':         msg['user_id'],
            'login_id':        msg['login_id'],
            'message':         msg['message'],
            'messageSequence': msg['messageSequence'],
            'created_at':      msg['created_at'].isoformat(),  # or str(msg['created_at'])
            'study_id':        room
        })


    emit('status', {'msg': f'{login_id}님이 입장했습니다.'}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['study_id']
    message = data['message']
    user_id = data['user_id']          # ✅ session 대신
    login_id = data['login_id']        # ✅ session 대신

    cur = mysql.connection.cursor()
    cur.execute("SELECT COALESCE(MAX(messageSequence), 0) + 1 AS seq FROM Chat WHERE study_id = %s", (room,))
    seq = cur.fetchone()['seq']
    cur.execute(
        "INSERT INTO Chat (study_id, user_id, message, messageSequence) VALUES (%s, %s, %s, %s)",
        (room, user_id, message, seq)
    )
    mysql.connection.commit()
    # 방금 INSERT 된 row의 created_at 을 다시 조회
    cur.execute("""
        SELECT created_at
        FROM Chat
        WHERE study_id = %s AND messageSequence = %s
    """, (room, seq))
    created_at = cur.fetchone()['created_at']
    cur.close()
    emit('message', {
        'user_id':         user_id,
        'login_id':        login_id,
        'message':         message,
        'messageSequence': seq,
        'created_at':      created_at.isoformat(),
        'study_id':        room
    }, room=room)



@socketio.on('leave')
def handle_leave(data):
    room = data['study_id']
    user_id = session['user_id']
    login_id = session['login_id']
    # cur = mysql.connection.cursor()
    # cur.execute("SELECT MAX(messageSequence) FROM Chat WHERE study_id = %s", (room,))
    # last_seq = cur.fetchone()['MAX(messageSequence)'] or 0
    # cur.execute("UPDATE UserRoomStatus SET first_messageSequence = %s WHERE user_id = %s AND study_id = %s",
    #             (last_seq, user_id, room))
    # mysql.connection.commit()
    # cur.close()
    leave_room(room)
    emit('status', {'msg': f'{login_id}님이 퇴장했습니다.'}, room=room)

# ================= 서버 실행 =================
if __name__ == '__main__':
    socketio.run(app, debug=True)
