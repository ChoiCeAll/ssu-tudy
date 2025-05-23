from flask import Flask, request, jsonify, session, render_template, abort, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL 설정
#app.config['MYSQL_HOST'] = 'mysql'
app.config['MYSQL_HOST'] = 'localhost'  # 또는 '127.0.0.1'

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'study'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
socketio = SocketIO(app)

# HTML 라우트
@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/register')
def show_register_form():
    return render_template('register.html')

@app.route('/mypage')
def show_mypage():
    return render_template('mypage.html')

@app.route('/notifications')
def show_notifications():
    return render_template('notifications.html')


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



# 스터디 목록 조회
@app.route('/studies')
def study_list():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    keyword = request.args.get('keyword', '').strip()
    hashtag = request.args.get('hashtag', '').strip()
    sort = request.args.get('sort', 'recent')

    def build_query(leader_condition):
        where_clauses = ["is_active = TRUE"]
        params = []

        if leader_condition == 'mine':
            where_clauses.append("leader_id = %s")
            params.append(user_id)
        else:
            where_clauses.append("leader_id != %s")
            params.append(user_id)

        if keyword:
            where_clauses.append("(title LIKE %s OR description LIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        if hashtag:
            where_clauses.append("hashtags LIKE %s")
            params.append(f"%{hashtag}%")

        where_sql = " AND ".join(where_clauses)

        order_sql = "created_at DESC" if sort == "recent" else "title ASC"
        query = f"SELECT study_id, title, description FROM Study WHERE {where_sql} ORDER BY {order_sql}"
        return query, params

    cur = mysql.connection.cursor()
    my_query, my_params = build_query('mine')
    cur.execute(my_query, my_params)
    my_studies = cur.fetchall()

    other_query, other_params = build_query('others')
    cur.execute(other_query, other_params)
    other_studies = cur.fetchall()
    cur.close()

    return render_template('study_list.html',
                           my_studies=my_studies,
                           other_studies=other_studies,
                           keyword=keyword,
                           hashtag=hashtag,
                           sort=sort)



# 스터디 상세보기
@app.route('/studies/<int:study_id>')
def study_detail(study_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # 스터디 정보 조회
    cur.execute("SELECT * FROM Study WHERE study_id = %s", (study_id,))
    study = cur.fetchone()

    # 댓글 목록 조회
    cur.execute("""
        SELECT c.content, u.login_id, c.created_at, c.author_id, c.comment_id 
        FROM Comment c 
        JOIN User u ON c.author_id = u.user_id 
        WHERE c.study_id = %s AND c.is_active = TRUE
    """, (study_id,))
    comments = cur.fetchall()

    # 현재 사용자가 이미 신청한 스터디인지 확인
    cur.execute("SELECT * FROM StudyMember WHERE study_id = %s AND user_id = %s", (study_id, user_id))
    is_applied = cur.fetchone() is not None

    cur.close()

    is_author = (study['leader_id'] == user_id)

    return render_template(
        'study_detail.html',
        study=study,
        study_id=study_id,
        is_author=is_author,
        is_applied=is_applied,
        comments=comments
    )

# 스터디 생성

@app.route('/studies/create', methods=['GET', 'POST'])
def study_create():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        raw_tags = request.form['hashtags']
        open_kakao_link = request.form.get('open_kakao_link', '')
        max_members = request.form['max_members']
        leader_id = session['user_id']

        # 해시태그 정규화 처리 (공백 제거, '#' 제거, 소문자 변환)
        tags = [tag.strip().lstrip('#').lower() for tag in raw_tags.split(',') if tag.strip()]
        normalized_hashtags = ','.join(tags)

        cur = mysql.connection.cursor()
        try:
            # 스터디 정보 저장
            cur.execute("""
                INSERT INTO Study (title, description, leader_id, hashtags, open_kakao_link, max_members, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE)
            """, (title, description, leader_id, normalized_hashtags, open_kakao_link, max_members))
            study_id = cur.lastrowid

            # 관심 해시태그 기반 알림 전송
            if tags:
                conditions = " OR ".join(["m.hashtags LIKE %s" for _ in tags])
                params = [f"%{tag}%" for tag in tags]

                cur.execute(f"""
                    SELECT u.user_id
                    FROM MyPage m
                    JOIN User u ON m.user_id = u.user_id
                    WHERE ({conditions}) AND u.user_id != %s
                """, params + [leader_id])

                matched_users = cur.fetchall()
                for user in matched_users:
                    msg = f"[{title}] 관심 해시태그와 일치하는 새 스터디가 등록되었습니다!"
                    cur.execute("""
                        INSERT INTO Notification (user_id, message, study_id, is_read, created_at)
                        VALUES (%s, %s, %s, FALSE, NOW())
                    """, (user['user_id'], msg, study_id))

            mysql.connection.commit()
            flash('스터디 생성 완료')
            return redirect(url_for('study_list'))

        except Exception as e:
            mysql.connection.rollback()
            flash(f'스터디 생성 실패: {str(e)}')

        finally:
            cur.close()

    return render_template('study_create.html')


# 스터디 수정
@app.route('/studies/<int:study_id>/edit', methods=['GET', 'POST'])
def study_edit(study_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Study WHERE study_id = %s", (study_id,))
    study = cur.fetchone()

    if not study or study['leader_id'] != session['user_id']:
        flash('수정 권한이 없습니다.')
        return redirect(url_for('study_detail', study_id=study_id))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        hashtags = request.form['hashtags']
        open_kakao_link = request.form.get('open_kakao_link', '')
        max_members = request.form['max_members']

        try:
            cur.execute("""
                UPDATE Study
                SET title=%s, description=%s, hashtags=%s, open_kakao_link=%s, max_members=%s
                WHERE study_id = %s
            """, (title, description, hashtags, open_kakao_link, max_members, study_id))
            mysql.connection.commit()
            flash('스터디 수정 완료')
            return redirect(url_for('study_detail', study_id=study_id))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'수정 실패: {str(e)}')
        finally:
            cur.close()

    return render_template('study_edit.html', study=study, study_id=study_id)

# 스터디 삭제
@app.route('/studies/<int:study_id>/delete', methods=['POST'])
def delete_study(study_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT leader_id FROM Study WHERE study_id = %s", (study_id,))
    study = cur.fetchone()

    if not study or study['leader_id'] != session['user_id']:
        flash('삭제 권한이 없습니다.')
        return redirect(url_for('study_detail', study_id=study_id))

    try:
        cur.execute("UPDATE Study SET is_active = FALSE WHERE study_id = %s", (study_id,))
        mysql.connection.commit()
        flash('스터디 삭제 완료')
        return redirect(url_for('study_list'))
    except Exception as e:
        mysql.connection.rollback()
        flash(f'삭제 실패: {str(e)}')
    finally:
        cur.close()

# 댓글 추가
@app.route('/studies/<int:study_id>/comments', methods=['POST'])
def add_comment(study_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    content = request.form['content']
    author_id = session['user_id']

    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO Comment (study_id, author_id, content, is_active) VALUES (%s, %s, %s, TRUE)",
                    (study_id, author_id, content))
        mysql.connection.commit()
        flash('댓글 등록 완료')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'댓글 등록 실패: {str(e)}')
    finally:
        cur.close()

    return redirect(url_for('study_detail', study_id=study_id))

# 댓글 수정
@app.route('/studies/<int:study_id>/comments/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(study_id, comment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT content, author_id FROM Comment WHERE comment_id = %s", (comment_id,))
    comment = cur.fetchone()

    if not comment or comment['author_id'] != session['user_id']:
        flash('수정 권한이 없습니다.')
        cur.close()
        return redirect(url_for('study_detail', study_id=study_id))

    if request.method == 'POST':
        new_content = request.form['content']
        try:
            cur.execute("UPDATE Comment SET content = %s WHERE comment_id = %s", (new_content, comment_id))
            mysql.connection.commit()
            flash('댓글 수정 완료')
            return redirect(url_for('study_detail', study_id=study_id))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'댓글 수정 실패: {str(e)}')
        finally:
            cur.close()
    else:
        cur.close()
        return render_template(
            'edit_comment.html',
            study_id=study_id,
            comment_id=comment_id,
            content=comment['content']
        )


# 댓글 삭제
@app.route('/studies/<int:study_id>/comments/<int:comment_id>/delete', methods=['POST'])
def delete_comment(study_id, comment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE Comment SET is_active = FALSE WHERE comment_id = %s", (comment_id,))
        mysql.connection.commit()
        flash('댓글 삭제 완료')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'댓글 삭제 실패: {str(e)}')
    finally:
        cur.close()

    return redirect(url_for('study_detail', study_id=study_id))

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
@app.route('/study/<int:study_id>/apply', methods=['POST'])
def apply_to_study(study_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # 이미 신청했는지 확인
    cur.execute("SELECT * FROM StudyMember WHERE study_id = %s AND user_id = %s", (study_id, user_id))
    if cur.fetchone():
        cur.close()
        flash('⚠ 이미 신청한 스터디입니다.')
        return redirect(url_for('study_detail', study_id=study_id))

    # 신청 insert
    cur.execute("INSERT INTO StudyMember (study_id, user_id, is_approved) VALUES (%s, %s, 0)", (study_id, user_id))
    study_member_id = cur.lastrowid

    # 스터디 정보 가져오기
    cur.execute("SELECT leader_id, title FROM Study WHERE study_id = %s", [study_id])
    study = cur.fetchone()

    # 신청자 이름/학과 포함 알림 생성
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
    flash('✅ 스터디 신청이 완료되었습니다!')
    return redirect(url_for('study_detail', study_id=study_id))

@app.route('/study/application/<int:study_member_id>', methods=['PUT'])
def decide_application(study_member_id):
    if 'user_id' not in session:
        return abort(403)

    # 승인 or 거절 값 받기
    decision = request.get_json().get('decision')
    if decision not in ['approve', 'reject']:
        return jsonify({'error': 'invalid decision'}), 400

    cur = mysql.connection.cursor()

    # 신청 정보 및 스터디 정보 확인
    cur.execute("""
        SELECT sm.user_id, sm.study_id, s.leader_id, s.title, s.open_kakao_link
        FROM StudyMember sm
        JOIN Study s ON sm.study_id = s.study_id
        WHERE sm.study_member_id = %s
    """, [study_member_id])
    result = cur.fetchone()

    if not result or result['leader_id'] != session['user_id']:
        cur.close()
        return abort(403)

    # 신청자 정보
    applicant_id = result['user_id']
    study_title = result['title']
    study_id = result['study_id']
    link = result['open_kakao_link'] or '(스터디장에게 문의해주세요)'

    # 승인 or 거절 처리
    if decision == 'approve':
        cur.execute("UPDATE StudyMember SET is_approved = 1 WHERE study_member_id = %s", [study_member_id])
        msg = f"[{study_title}] 스터디 신청이 승인되었습니다! 오픈카카오 링크: {link}"
    else:
        cur.execute("DELETE FROM StudyMember WHERE study_member_id = %s", [study_member_id])
        msg = f"[{study_title}] 스터디 신청이 거절되었습니다."

    # 신청자에게 알림 전송
    cur.execute("""
        INSERT INTO Notification (user_id, message, study_id, is_read, created_at)
        VALUES (%s, %s, %s, FALSE, NOW())
    """, (applicant_id, msg, study_id))

    mysql.connection.commit()
    cur.close()
    return jsonify({'message': '신청이 처리되었습니다.'})


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
    cur.execute("SELECT COALESCE(MAX(messageSequence), 0) FROM Chat WHERE study_id = %s", (room,))
    last_seq = cur.fetchone()['COALESCE(MAX(messageSequence), 0)']
    next_seq = last_seq + 1
    cur.execute("""
        INSERT INTO UserRoomStatus (user_id, study_id, first_messageSequence)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE first_messageSequence = VALUES(first_messageSequence)
    """, (user_id, room, next_seq))
    mysql.connection.commit()
    cur.execute("""
        SELECT c.user_id, u.login_id, c.message, c.messageSequence
        FROM Chat c JOIN User u ON c.user_id = u.user_id
        WHERE c.study_id = %s AND c.messageSequence >= %s
        ORDER BY c.messageSequence ASC
    """, (room, next_seq))
    for msg in cur.fetchall():
        emit('message', {
            'login_id': msg['login_id'],
            'message': msg['message'],
            'messageSequence': msg['messageSequence']
        })
    cur.close()
    emit('status', {'msg': f'{login_id}님이 입장했습니다.'}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['study_id']
    message = data['message']
    user_id = session['user_id']
    login_id = session['login_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT COALESCE(MAX(messageSequence), 0) + 1 AS seq FROM Chat WHERE study_id = %s", (room,))
    seq = cur.fetchone()['seq']
    cur.execute("INSERT INTO Chat (study_id, user_id, message, messageSequence) VALUES (%s, %s, %s, %s)",
                (room, user_id, message, seq))
    mysql.connection.commit()
    cur.close()
    emit('message', {
        'login_id': login_id,
        'message': message,
        'messageSequence': seq
    }, room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['study_id']
    user_id = session['user_id']
    login_id = session['login_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT MAX(messageSequence) FROM Chat WHERE study_id = %s", (room,))
    last_seq = cur.fetchone()['MAX(messageSequence)'] or 0
    cur.execute("UPDATE UserRoomStatus SET first_messageSequence = %s WHERE user_id = %s AND study_id = %s",
                (last_seq, user_id, room))
    mysql.connection.commit()
    cur.close()
    leave_room(room)
    emit('status', {'msg': f'{login_id}님이 퇴장했습니다.'}, room=room)

# ================= 서버 실행 =================
if __name__ == '__main__':
    socketio.run(app, debug=True)
