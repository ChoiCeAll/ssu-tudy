<template>
    <div class="layout">
        <header class="header">
            <div class="logo">
                <a href="/" class="logo-link">SSU-TUDY</a>
            </div>
            <div class="header-right">
                <span v-if="!state.isLoggedIn" @click="openLoginModal" class="clickable">로그인</span>
                <span v-else>
                    <span class="clickable" @click="logout">로그아웃</span>
                    <span class="icon clickable" @click="togglePanel('alarm')">🔔</span>
                    <span class="icon clickable" @click="togglePanel('chat')">💬</span>
                    <span class="icon clickable" @click="togglePanel('profile')">👤</span>
                </span>
            </div>
        </header>

        <main class="main">
            <slot />
        </main>

        <footer class="footer">
            <h3 class="footer-section-title">자주 찾는 학교 사이트</h3>
            <div class="footer-links-grid-vertical">
                <!-- 1열 -->
                <div class="footer-col">
                    <a href="https://saint.ssu.ac.kr/irj/portal" target="_blank" rel="noopener">유세인트</a>
                    <a href="https://canvas.ssu.ac.kr/" target="_blank" rel="noopener">스마트캠퍼스 LMS</a>
                </div>
                <!-- 2열 -->
                <div class="footer-col">
                    <a href="https://scatch.ssu.ac.kr/%ea%b3%b5%ec%a7%80%ec%82%ac%ed%95%ad/?f&category=%ED%95%99%EC%82%AC&keyword" target="_blank" rel="noopener">학사 공지사항</a>
                    <a href="https://fun.ssu.ac.kr/" target="_blank" rel="noopener">비교과(FUN) 시스템</a>
                </div>
                <!-- 3열 -->
                <div class="footer-col">
                    <a href="https://counsel.ssu.ac.kr/" target="_blank" rel="noopener">학생상담센터</a>
                    <a href="https://job.ssu.ac.kr/" target="_blank" rel="noopener">취업진로센터</a>
                </div>
                <!-- 4열 -->
                <div class="footer-col">
                    <a href="https://oasis.ssu.ac.kr/library-services/smuf/reading-rooms" target="_blank" rel="noopener">도서관 열람실/좌석 예약</a>
                    <a href="https://oasis.ssu.ac.kr/library-services/smuf/rooms" target="_blank" rel="noopener">도서관 세미나실/공간 예약</a>
                </div>
            </div>
            <div class="footer-content">
                &copy; 2025 SSU-TUDY. All rights reserved.
            </div>
        </footer>



        <!-- 사이드 패널 -->
        <div class="side-panel" :class="{ open: state.showPanel }">
            <div class="side-header">
                <div class="side-header-top">
                    <span v-if="state.panelType === 'alarm'">알림</span>
                    <span v-else-if="state.panelType === 'chat'">채팅방</span>
                    <span v-else>내 정보</span>
                    <button class="close-side" @click="closePanel">»</button>
                </div>
                <template v-if="state.panelType === 'alarm'">
                    <div class="side-header-sub">
                        📭 소식이 생기면 여기에서 알려드릴게요!
                    </div>
                </template>
                <template v-else-if="state.panelType === 'chat'">
                    <div class="side-header-sub">
                        🤝 채팅방에서 사람들과 소통해보세요!
                    </div>
                </template>
                <template v-else>
                    <div class="side-header-sub">
                        🛠️ 나를 위한 설정은 언제나 이곳에서!
                    </div>
                </template>
            </div>
            <div class="side-content">
                <div v-if="state.panelType === 'alarm'">
                    <template v-if="state.alarms.length === 0">
                        <span>😌 모든 것이 평온해요. 알림이 없습니다.</span>
                    </template>
                    <template v-else>
                        <div class="alarm-list">
                            <div
                                class="alarm-item"
                                v-for="alarm in state.alarms"
                                :key="alarm.id"
                                :class="{ unread: !alarm.is_read }"
                            >
                                <div class="alarm-message">{{ alarm.message }}</div>
                                <div class="alarm-time">{{ alarm.time }}</div>
                            </div>
                        </div>
                    </template>
                </div>

                <div v-else-if="state.panelType === 'chat'">
                    <div class="chat-room-list">
                        <div
                            v-for="room in state.chatRooms"
                            :key="room.id"
                            class="chat-room-item"
                            @click="openChat(room)"
                        >
                            💬 {{ room.name }}
                        </div>
                    </div>
                </div>
                <div v-else>
                    <div class="profile-item">
                        <label>닉네임</label>
                        <div class="field">
                            <input v-if="state.editMode" v-model="state.editProfile.nickname" />
                            <span v-else>{{ state.profile.nickname }}</span>
                        </div>
                    </div>

                    <div class="profile-item">
                        <label>학번</label>
                        <div class="field">
                            <input v-if="state.editMode" v-model="state.editProfile.studentId" />
                            <span v-else>{{ state.profile.studentId }}</span>
                        </div>
                    </div>

                    <div class="profile-item">
                        <label>전공</label>
                        <div class="field">
                            <input v-if="state.editMode" v-model="state.editProfile.major" />
                            <span v-else>{{ state.profile.major }}</span>
                        </div>
                    </div>

                    <div class="profile-item">
                        <label>알림 해시태그</label>
                        <div class="hashtags">
                            <template v-if="state.editMode">
                                <div v-for="(tag, index) in state.editProfile.hashtagList" :key="index" class="tag-input">
                                    <input v-model="state.editProfile.hashtagList[index]" />
                                </div>
                                <button @click="addHashtag">+ 해시태그 추가</button>
                            </template>
                            <template v-else>
                                <div v-for="(tag, index2) in state.profile.hashtagList" :key="index2" class="tag-input">
                                    <span>{{ state.profile.hashtagList[index2] }}</span>
                                </div>
                            </template>
                        </div>
                    </div>

                    <div class="edit-buttons" v-if="state.panelType === 'profile'">
                        <button v-if="!state.editMode" @click="toggleEdit">✏️ 수정</button>
                        <div v-else>
                            <button @click="saveEdit">✔️ 저장</button>
                            <button @click="cancelEdit">❌ 취소</button>
                        </div>
                    </div>

                </div>
            </div>
        </div>

        <!-- 오버레이 클릭 시 패널 닫기 -->
        <div v-if="state.showPanel" class="overlay" @click="closePanel"></div>

        <!-- 로그인 모달 -->
        <div v-if="state.showLogin" class="modal" @click.self="closeLoginModal">
            <div class="modal-content">
                <button class="close-btn" @click="closeLoginModal">❌</button>
                <h2>로그인</h2>
                <div>
                    <label for="id">ID</label>
                    <input type="text" v-model="state.id" />

                    <label for="password">PW</label>
                    <input type="password" v-model="state.pw" @keyup.enter="login" />

                    <button type="button" class="login-btn" @click="login">로그인</button>
                </div>
                <div>
                    <p style="text-align: left;">계정이 없으신가요? <a href="#" @click.prevent="openRegisterModal">회원가입</a></p>
                    <p style="text-align: left;">비밀번호를 잊으셨나요? <a href="#" @click.prevent="openResetModal">비밀번호 재설정</a></p>
                </div>                
            </div>
        </div>

        <div v-if="state.showRegister" class="modal" @click.self="closeRegisterModal">
            <div class="modal-content">
                <button class="close-btn" @click="closeRegisterModal">❌</button>
                <h2>회원가입</h2>

                <template v-if="state.registerStep === 1">
                    <label>ID</label>
                    <div class="field">
                        <input type="text" v-model="state.register.id" />
                        <button class="small-btn" @click="checkDuplicateId">아이디 확인</button>
                    </div>

                    <label>PW</label>
                    <input type="password" v-model="state.register.pw" />

                    <button class="login-btn" @click="checkIdAndNextStep">다음</button>
                </template>

                <template v-else>
                    <label>닉네임 *</label>
                    <input type="text" v-model="state.register.nickname" placeholder="슝슝이25" />

                    <label>학번 *</label>
                    <input type="text" v-model="state.register.studentId" placeholder="20252025" />

                    <label>전공 *</label>
                    <input type="text" v-model="state.register.major" placeholder="AI융합학과" />

                    <label>알림 해시태그 (선택)</label>
                    <div class="hashtags">
                        <div v-for="(tag, index) in state.register.hashtagList" :key="index" class="tag-input">
                            <input v-model="state.register.hashtagList[index]" />
                        </div>
                        <button @click="addRegisterHashtag">+ 해시태그 추가</button>
                    </div>

                    <button class="login-btn" @click="submitRegister">제출</button>
                </template>
            </div>
        </div>

        <!-- 비밀번호 재설정 모달 -->
        <div v-if="state.showReset" class="modal" @click.self="closeResetModal">
            <div class="modal-content">
                <button class="close-btn" @click="closeResetModal">❌</button>
                <h2>비밀번호 재설정</h2>

                <label>ID</label>
                <input type="text" v-model="state.reset.login_id" />

                <label>학번</label>
                <input type="text" v-model="state.reset.student_id" />

                <label>새 비밀번호</label>
                <input type="password" v-model="state.reset.new_password" />

                <button class="login-btn" @click="resetPassword">비밀번호 변경</button>
            </div>
        </div>

        <!-- 채팅방 -->
        <div v-if="state.showChatPopup" class="chat-popup" ref="chatPopupRef">
            <div class="chat-header" ref="chatHeaderRef">
                <span>{{ state.activeChatRoom?.name }}</span>
                <button @click="closeChatPopup">❌</button>
            </div>
            <div class="chat-body">
                <div
                    v-for="(msg, i) in state.chatMessages[state.activeChatRoom?.id]"
                    :key="i"
                    :class="['chat-msg-container', msg.from === state.userId ? 'mine' : 'theirs']"
                >
                    <!-- 프로필 원 -->
                    <div class="chat-profile-wrapper" v-if="msg.from !== state.userId">
                        <div
                            class="chat-profile"
                            :style="{ backgroundColor: getProfileColor(msg.from) }"
                        >
                            {{ getProfileInitial(msg.from) }}
                        </div>
                        <div class="custom-tooltip">
                            <div><strong>{{ userMap[msg.from]?.nickname }}</strong></div>
                            <div>{{ userMap[msg.from]?.studentId }}</div>
                            <div>{{ userMap[msg.from]?.major }}</div>
                        </div>
                    </div>

                    <!-- 메시지 내용 -->
                    <div class="chat-msg-wrapper">
                        <div class="chat-msg" :class="msg.from === state.userId ? 'sent' : 'received'">
                            {{ msg.text }}
                        </div>
                        <div class="chat-time">{{ formatTime(msg.timestamp) }}</div>
                    </div>


                </div>
            </div>
            <div class="chat-footer">
                <input type="text" v-model="state.newMessage" @keyup.enter="sendMessage" placeholder="메시지를 입력하세요" />
                <button @click="sendMessage">➤</button>
            </div>
        </div>

    </div>
</template>

<script setup>
import { reactive, onMounted, ref, nextTick, watchEffect } from 'vue'
import { useToast } from 'vue-toastification'
import axios from 'axios'

const toast = useToast()
const chatPopupRef = ref(null)
const chatHeaderRef = ref(null)

const state = reactive({
    isLoggedIn: false,
    showLogin: false,
    userName: '',
    id: '',
    pw: '',
    showRegister: false, // 회원가입 모달
    registerStep: 1,     // 1단계: ID/PW, 2단계: 프로필
    checkDuplicateFlag: false,
    register : {
        id: '',
        pw: '',
        nickname: '',
        studentId: '',
        major: '',
        hashtags: '',
        hashtagList: ['#']
    },
    showPanel: false,
    panelType: '', // 'alarm' 'chat' 'profile'
    alarms: [],
    profile: {
        nickname: '',
        studentId: '',
        major: '',
        hashtagList: ['#']
    },
    editMode: false,
    editProfile: {
        nickname: '',
        studentId: '',
        major: '',
        hashtagList: ['#']
    },
    //일단 mock
    chatRooms: [
        { id: 1, name: 'AI융합스터디' },
        { id: 2, name: '웹프론트엔드' },
    ],
    showChatPopup: false,
    activeChatRoom: null,
    chatMessages: {
        1: [
            { from: 1, text: '안녕하세요!', timestamp: new Date(Date.now() - 12000 * 60) },
            { from: 2, text: '반갑습니다', timestamp: new Date(Date.now() - 1000 * 60) }
        ],
        2: [
            { from: 1, text: 'Vue 공부중이에요', timestamp: new Date(Date.now() - 1000 * 60) }
        ]
    },
    newMessage: '',
    userId: '',
    userName: '',
    showReset: false, // 비밀번호 재설정 모달
    reset: {
        login_id: '',
        student_id: '',
        new_password: ''
    }
})

// Mock: 사용자 정보
const userMap = {
  1: { nickname: 'choi123', studentId: '20231234', major: 'AI융합학과' },
  2: { nickname: 'kim456', studentId: '20231235', major: '소프트웨어' },
  3: { nickname: 'lee789', studentId: '20231236', major: '정보보안' },
}

// 각 유저에 고유 색상 매핑 (단순 해시)
const getProfileColor = (id) => {
  const colors = ['#42b983', '#ff6b6b', '#f0ad4e', '#5bc0de', '#8e44ad']
  return colors[id % colors.length]
}

// 프로필 원 안에 보여줄 이니셜 (닉네임 첫글자)
const getProfileInitial = (id) => {
  return userMap[id]?.nickname.charAt(0).toUpperCase() || '?'
}

onMounted(async () => {
    try {
        const res = await axios.get('/api/session-check', { withCredentials: true })
        if (res.data.is_logged_in) {
            state.isLoggedIn = true
            state.userId = res.data.user_id
            state.userName = res.data.login_id
        }
    } catch (e) {
        console.error('세션 확인 실패:', e)
    }
    setInterval(() => {
        if (state.isLoggedIn) {
            fetchAlarms()
        }
    }, 10000) // 10초마다
})

watchEffect(() => {
  if (state.showChatPopup) {
    nextTick(() => {
        const popup = chatPopupRef.value
        const header = chatHeaderRef.value
        if (!popup || !header) return

        popup.style.position = 'absolute'
        if (!popup.style.left) popup.style.left = '100px'
        if (!popup.style.top) popup.style.top = '100px'
        popup.style.zIndex = 9999


        let isDragging = false
        let offsetX = 0
        let offsetY = 0

        const onMouseDown = (e) => {
            isDragging = true
            const rect = popup.getBoundingClientRect()
            offsetX = e.clientX - rect.left
            offsetY = e.clientY - rect.top
        }

        const onMouseMove = (e) => {
            if (!isDragging) return
            popup.style.left = `${e.clientX - offsetX}px`
            popup.style.top = `${e.clientY - offsetY}px`
        }

        const onMouseUp = () => {
            isDragging = false
        }

        header.addEventListener('mousedown', onMouseDown)
        document.addEventListener('mousemove', onMouseMove)
        document.addEventListener('mouseup', onMouseUp)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                state.showChatPopup = false
                state.newMessage = ''
            }
        })

        // 💡 remove listeners when popup closes (안그러면 중복됨)
        watchEffect((onInvalidate) => {
            onInvalidate(() => {
                header.removeEventListener('mousedown', onMouseDown)
                document.removeEventListener('mousemove', onMouseMove)
                document.removeEventListener('mouseup', onMouseUp)
            })
        })
    })
  }
})

function openLoginModal() {
    state.showLogin = true
}

function closeLoginModal() {
    state.showLogin = false
    state.id = ''
    state.pw = ''
}

function openRegisterModal() {
    state.showLogin = false
    state.showRegister = true
    state.registerStep = 1
    state.register = {
        id: '',
        pw: '',
        nickname: '',
        studentId: '',
        major: '',
        hashtags: '',
        hashtagList: ['#']
    }
}
function closeRegisterModal() {
    state.showRegister = false
    state.register = {
        id: '',
        pw: '',
        nickname: '',
        studentId: '',
        major: '',
        hashtags: '',
        hashtagList: ['#']
    }
}
function addRegisterHashtag() {
    state.register.hashtagList = [...state.register.hashtagList, '#']
    toast.success('해시태그 추가 완료.')
}

function checkIdAndNextStep() {
    if (!state.checkDuplicateFlag) {
        toast.error('아이디 중복 확인을 먼저 해주세요.')
        return
    }

    const { id, pw } = state.register
    if (!id.trim() || !pw.trim()) {
        toast.error('ID와 PW는 필수입니다.')
        return
    }

    toast.success('다음 단계로 이동합니다.')
    state.registerStep = 2

}

async function checkDuplicateId() {
    const id = state.register.id.trim()
    if (!id) {
        toast.error('ID를 입력해주세요.')
        return
    }

    try {
        const res = await axios.post(
            '/api/check-id',
            { login_id: id }, // ✅ 이게 body
            {
                headers: {
                    'Content-Type': 'application/json' // ✅ 이건 config
                }
            }
        )

        if (res.data.exists) {
            toast.error('이미 존재하는 ID입니다.')
            state.checkDuplicateFlag = false
        } else {
            toast.success('사용 가능한 ID입니다.')
            state.checkDuplicateFlag = true
        }
    } catch (error) {
        console.error(error)
        toast.error('서버 오류가 발생했습니다.')
    }
}

async function submitRegister() {
    const { id, pw: password, nickname, studentId, major, hashtagList } = state.register

    if (!id.trim() || !password.trim() || !nickname.trim() || !studentId.trim() || !major.trim()) {
        toast.error('아이디, 비밀번호, 닉네임, 학번, 전공은 필수입니다.')
        return
    }

    // ✅ hashtagList → hashtags 변환
    const hashtags = hashtagList
        .map(tag => tag.trim())                         // 공백 제거
        .map(tag => tag === '#' ? '' : tag.replace(/^#/, '').toLowerCase()) // #만 있으면 빈 문자열, 아니면 # 제거
        .filter(tag => tag)                             // 빈 문자열 제거
        .join(',')                                       // 콤마로 join

    try {
        const res = await axios.post('/api/register', {
            login_id: id,
            password,
            name: nickname,
            student_id: studentId,
            major,
            hashtags  // ✅ 변환된 문자열 전송
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        })

        toast.success('회원가입이 완료되었습니다.')
        console.log('서버 응답:', res.data)

        state.showRegister = false
        state.showLogin = true
    } catch (err) {
        console.error(err)        
        if (err.response?.data?.error) {
            toast.error(err.response.data.error)
        } else {
            toast.error('서버 오류가 발생했습니다.')
        }
    }
    state.register = {
        id: '',
        pw: '',
        nickname: '',
        studentId: '',
        major: '',
        hashtags: '',
        hashtagList: ['#']
    }
}

function openResetModal() {
  state.showLogin = false
  state.showReset = true
  state.reset = {
    login_id: '',
    student_id: '',
    new_password: ''
  }
}

function closeResetModal() {
  state.showReset = false
  state.reset = {
    login_id: '',
    student_id: '',
    new_password: ''
  }
}

async function resetPassword() {
  const { login_id, student_id, new_password } = state.reset
  if (!login_id.trim() || !student_id.trim() || !new_password.trim()) {
    toast.error('모든 항목을 입력해주세요.')
    return
  }

  try {
    const res = await axios.post('/api/reset-password', {
      login_id, student_id, new_password
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    })

    toast.success(res.data.message || '비밀번호가 재설정되었습니다.')
    closeResetModal()
    state.showLogin = true
  } catch (err) {
    console.error(err)
    if (err.response?.data?.error) {
      toast.error(err.response.data.error)
    } else {
      toast.error('서버 오류가 발생했습니다.')
    }
  }
}

async function login() {
    const login_id = state.id.trim()
    const password = state.pw.trim()

    if (!login_id || !password) {
        toast.error('ID와 비밀번호를 모두 입력해주세요.')
        return
    }

    try {
        const res = await axios.post('/api/login', {
            login_id,
            password
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        })

        // 로그인 성공
        state.userId = res.data.user_id
        state.userName = res.data.login_id
        state.isLoggedIn = true
        state.showLogin = false
        toast.success('로그인 완료!')
    } catch (err) {
        console.error(err)
        if (err.response?.status === 401) {
            toast.error('아이디 또는 비밀번호가 잘못되었습니다.')
        } else {
            toast.error('서버 오류가 발생했습니다.')
        }
    }
    state.id = ''
    state.pw = ''
}

async function logout() {
    try {
        await axios.post('/api/logout', {}, { withCredentials: true })
        state.isLoggedIn = false
        toast.success('로그아웃 되었습니다!')
    } catch (e) {
        console.error('로그아웃 실패:', e)
        toast.error('로그아웃 실패')
    }
}


async function togglePanel(type){
    if (state.showPanel && state.panelType === type) {
        state.panelType = ''
        state.showPanel = false
    } else {
        state.panelType = type
        state.showPanel = true
        
        if (type === 'alarm') {
            await fetchAlarms() // 알람만 열릴 때 호출
        } else if (type === 'profile') {
            await fetchMyPage()
        }
    }
}

function toggleEdit() {
    state.editProfile = JSON.parse(JSON.stringify(state.profile))
    state.editMode = true
}

function cancelEdit() {
    state.editProfile = {
        nickname: '',
        studentId: '',
        major: '',
        hashtagList: ['#']
    }
    state.editMode = false
}

async function saveEdit() {
    try {
        // 해시태그 정규화: '#' 제거, 소문자 변환, 공백 제거
        const hashtags = state.editProfile.hashtagList
            .map(tag => tag.trim().replace(/^#/, '').toLowerCase())
            .filter(Boolean)
            .join(',')

        const payload = {
            name: state.editProfile.nickname,
            major: state.editProfile.major,
            student_id: state.editProfile.studentId,
            hashtags
        }

        await axios.put(`/api/mypage/${state.userId}`, payload, {
            headers: { 'Content-Type': 'application/json' },
            withCredentials: true
        })
        state.profile = JSON.parse(JSON.stringify(state.editProfile))
        state.editMode = false
        toast.success('내 정보가 수정되었습니다.')
    } catch (err) {
        console.error('내정보 수정 실패:', err)
        toast.error('내 정보를 저장하는 데 실패했습니다.')
    }
}

function addHashtag() {
    state.editProfile.hashtagList = [...state.editProfile.hashtagList, '#']
    toast.success('해시태그 추가 완료.')
}

async function fetchAlarms() {
    if (!state.userId) return

    try {
        const res = await fetch(`/api/notifications/${state.userId}`, {
            credentials: 'include'
        })

        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)

        const data = await res.json()

        state.alarms = data.map(alarm => ({
            id: alarm.notification_id,
            message: alarm.message,
            is_read: alarm.is_read,
            time: formatKoreanTime(alarm.created_at)
        }))
    } catch (e) {
        console.error('알람 불러오기 실패:', e)
    }
}

async function fetchMyPage() {
    try {
        const res = await axios.get(`/api/mypage/${state.userId}`, { withCredentials: true })
        const data = res.data

        state.profile.nickname = data.name || '슝슝이25'
        state.profile.studentId = data.student_id || '20252025'
        state.profile.major = data.major || 'AI융합학과'
        state.profile.hashtagList = (data.hashtags || '')
            .split(',')
            .filter(Boolean)
            .map(tag => `#${tag.trim()}`)

        if (state.profile.hashtagList.length === 0) {
            state.profile.hashtagList = ['#']
        }
    } catch (e) {
        console.error('마이페이지 불러오기 실패:', e)
        toast.error('마이페이지 정보를 불러올 수 없습니다.')
    }
}


function closePanel() {
    state.showPanel = false
}

function openChat(room) {
    state.activeChatRoom = room
    state.showChatPopup = true
}

function closeChatPopup() {
    state.showChatPopup = false
    state.newMessage = ''
}

function sendMessage() {
    const text = state.newMessage.trim()
    if (!text || !state.activeChatRoom) return

    const roomId = state.activeChatRoom.id
    if (!state.chatMessages[roomId]) state.chatMessages[roomId] = []

    state.chatMessages[roomId].push({
        from: state.userId,
        text,
        timestamp: new Date()  // 시간 정보 추가
    })
    state.newMessage = ''

    // Mock 받은 메시지
    setTimeout(() => {
        state.chatMessages[roomId].push({
            from: 2,
            text: '답변이에요!',
            timestamp: new Date()
        })
    }, 1000)
}

function formatTime(date) {
    const d = new Date(date)
    let hours = d.getHours()
    const minutes = d.getMinutes().toString().padStart(2, '0')
    const period = hours >= 12 ? '오후' : '오전'
    hours = hours % 12 || 12
    return `${period} ${hours}:${minutes}`
}

function formatKoreanTime(isoString) {
    const d = new Date(isoString)
    const hour = d.getHours()
    const minutes = d.getMinutes().toString().padStart(2, '0')
    const period = hour < 12 ? '오전' : '오후'
    const formattedHour = hour % 12 || 12
    return `${period} ${formattedHour}:${minutes}`
}

</script>

<style>
    html, body {
        margin: 0;
        padding: 0;
        height: 100%;
        overflow-x: hidden;
    }

    *:not(input):not(textarea) {
        caret-color: transparent;
    }
    .layout {
        display: flex;
        flex-direction: column;
        min-height: 100vh; /* 전체 페이지 높이 */
    }

    .main {
        padding: 20px;
        flex: 1; /* 남은 공간만 차지 */
        /* ❌ overflow-y 제거 */
    }

    .header {
        position: sticky;
        top: 0;
        z-index: 1000;
        height: 64px;
        min-height: 64px;
        max-height: 64px;
        background-color: #fff !important;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 24px;
        border-bottom: 1px solid #ddd;
        transition: none !important;
    }

    .logo {
        font-weight: bold;
        font-size: 20px;
        color: #42b983;
    }
    .logo-link {
        color: #42b983;
        font-weight: bold;
        font-size: 20px;
        text-decoration: none;
    }

    .header-right {
        display: flex;
        align-items: center;
    }
    .header-right span {
        margin-left: 16px;
        font-size: 15px;
    }
    .icon {
        font-size: 18px;
    }
    .clickable {
        cursor: pointer;
        text-decoration: underline;
    }
    /* 사이드 패널 */
    .side-panel {
        position: fixed;
        top: 0;
        right: -300px;
        width: 300px;
        height: 100%;
        background-color: #fff;
        box-shadow: -2px 0 8px rgba(0, 0, 0, 0.2);
        transition: right 0.3s ease;
        z-index: 1001;
    }
    .side-panel.open {
        right: 0;
    }
    .side-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 16px;
        font-weight: bold;
        border-bottom: 1px solid #eee;
        flex-direction: column;
    }
    .side-header-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%
    }

    .side-header-sub {
        margin-top: 8px;
        font-size: 13px;
        color: #666;
    }

    .close-side {
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
    }
    .side-content {
        padding: 16px;
    }
    .profile-item {
        margin-bottom: 16px;
    }
    label {
        font-weight: bold;
        display: block;
        margin-bottom: 4px;
    }
    .field {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .field input {
        flex: 1;
        padding: 6px;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    .hashtags {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .tag-input input {
        padding: 6px;
        border: 1px solid #ccc;
        border-radius: 4px;
        width: 100%;
    }
    .edit-buttons {
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        margin-top: 24px;
    }

    .edit-buttons button {
        padding: 6px 12px;
        margin-left: 12px;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        cursor: pointer;
        background-color: #eee;
        transition: background-color 0.2s;
    }

    .edit-buttons button:hover {
        background-color: #ccc;
    }

    /* 오버레이 */
    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.2);
        z-index: 1000;
    }
    /* 모달 */
    .modal {
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999;
    }
    .modal-content {
        background: #fff;
        padding: 30px 40px;
        border-radius: 8px;
        width: 350px;
        position: relative;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }
    .close-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        background: transparent;
        border: none;
        font-size: 18px;
        cursor: pointer;
        padding: 0;
        line-height: 1;
    }
    .modal-content h2 {
        margin-top: 0;
        margin-bottom: 20px;
        font-size: 22px;
        text-align: center;
    }
    .modal-content label {
        display: block;
        margin: 10px 0 5px;
        font-weight: 600;
    }
    .modal-content input {
        width: 100%;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
        transition: border-color 0.2s;
    }
    .modal-content input:focus {
        border-color: #42b983;
        outline: none;
    }
    .login-btn {
        margin-top: 20px;
        width: 100%;
        padding: 10px;
        background-color: #42b983;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .modal-content button:hover {
        background-color: #369f6b;
    }
    .modal-content p {
        margin-top: 15px;
        font-size: 14px;
        text-align: center;
    }
    .modal-content a {
        color: #42b983;
        text-decoration: none;
        font-weight: 500;
    }
    .chat-popup {
        position: absolute;
        top: 100px;
        left: 100px;
        width: 400px;
        height: 600px;
        display: flex;
        flex-direction: column;
        background-image: url('../images/ssu-tudent.png'); /* 배경 이미지 추가 */
        background-size: cover; /* 이미지 크기에 맞게 채우기 */
        background-position: center; /* 중앙 정렬 */
        border-radius: 16px;
        overflow: visible;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        z-index: 1100;
        color: #fff;
    }
    .chat-popup::before {
        content: '';
        position: absolute;
        inset: 0;
        background: rgba(255, 255, 255, 0.2);
        z-index: 0;
    }
    .chat-popup > * {
        position: relative;
        z-index: 1;
    }
    /* 드래그용 헤더 */
    .chat-header {
        background-color: rgba(0, 0, 0, 0.6);
        padding: 10px 14px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
        cursor: move;
        color: #fff;
        font-size: 16px;
    }

    .chat-header button {
        background-color: transparent;
        border: 1px solid #fff;
        color: #fff;
        border-radius: 50%;
        width: 26px;
        height: 26px;
        font-size: 14px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background-color 0.2s;
    }
    .chat-header button:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    .chat-body {
        flex: 1;
        padding: 10px;
        overflow-y: auto;
        overflow-x: visible;
        position: relative;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .chat-msg-container {
        display: flex;
        align-items: flex-end;
        gap: 8px;
        position: relative; /* ✔️ 툴팁 위치 기준 */
    }

    .chat-msg-container.mine {
        flex-direction: row-reverse;
    }

    .chat-profile {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        color: white;
        font-size: 14px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: help;
    }
    .chat-msg {
        max-width: 80%;
        padding: 10px 14px;
        border-radius: 20px;
        line-height: 1.4;
        word-wrap: break-word;
        backdrop-filter: blur(4px);
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        color: #fff;
    }

    .chat-msg.sent {
        background: rgba(66, 185, 131, 0.85); /* 연녹색 반투명 */
        align-self: flex-end;
    }

    .chat-msg.received {
        background: rgba(68, 68, 68, 0.7);
        align-self: flex-start;
    }

    .chat-footer {
        display: flex;
        padding: 10px;
        background: rgba(0, 0, 0, 0.5);
    }

    .chat-footer input {
        flex: 1;
        padding: 10px 14px;
        border-radius: 20px;
        border: none;
        background: #fff;
        color: #333;
        outline: none;
        font-size: 14px;
    }

    .chat-footer button {
        margin-left: 8px;
        background: #42b983;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 18px;
        cursor: pointer;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background-color 0.2s;
    }
    .chat-footer button:hover {
        background-color: #369f6b;
    }

    .chat-room-list {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin: 0;
        padding: 0;
    }

    .chat-room-item {
        padding: 10px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 500;
        color: #333;
        width: 100%;
        box-sizing: border-box;
        transition: background-color 0.2s;
    }

    .chat-room-item:hover {
        background-color: #f0f0f0;
    }

    .chat-room-item:active {
        background-color: #e0e0e0;
    }

    .chat-profile-wrapper {
        position: relative;
        display: inline-block;
    }

    .custom-tooltip {
        position: absolute;
        bottom: 40px; /* 말풍선보다 위로 띄움 */
        left: 0;
        transform: translateX(-10%);
        background-color: #fff;
        color: #333;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 12px;
        white-space: nowrap;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s ease;
        z-index: 20;
        max-width: 250px;
    }

    /* 툴팁 보이게 */
    .chat-profile-wrapper:hover .custom-tooltip {
        opacity: 1;
    }

    /* 오른쪽 말풍선용 툴팁 정렬 반전 */
    .chat-msg-container.mine .chat-profile-wrapper .custom-tooltip {
        left: auto;
        right: 0;
        transform: translateX(10%);
    }
    .chat-footer input:focus {
        border: 2px solid #42b983;
        box-shadow: 0 0 6px rgba(66, 185, 131, 0.5);
        background-color: #fdfdfd;
        transition: all 0.2s;
    }
    .chat-msg-wrapper {
        display: flex;
        flex-direction: column;
    }

    .chat-time {
        font-size: 11px;
        background-color: rgba(0, 0, 0, 0.6);
        color: #fff;
        padding: 2px 6px;
        border-radius: 10px;
        margin-top: 4px;
        max-width: fit-content;
        font-weight: 500;
    }

    /* 내가 보낸 메시지: 오른쪽 정렬 */
    .chat-msg-container.mine .chat-time {
        align-self: flex-end;
    }

    /* 다른 사람이 보낸 메시지: 왼쪽 정렬 */
    .chat-msg-container.theirs .chat-time {
        align-self: flex-start;
    }

    .footer {
        padding: 16px;
        background-color: #f9f9f9;
        border-top: 1px solid #ddd;
        font-size: 14px;
        color: #666;
    }

    .footer-section-title {
        text-align: left;
        font-size: 16px;
        font-weight: 600;
        color: #444;
        margin-bottom: 20px;
        padding-left: 100px;
    }

    .footer-links-grid-vertical {
        display: flex;
        justify-content: flex-start;         /* 전체 열을 가운데 정렬 */
        gap: 20px 160px;                       /* 행,열 간격 */
        flex-wrap: wrap;                /* 줄바꿈 가능 (반응형 대비) */
        padding-bottom: 20px;
        padding-left: 100px;
    }

    .footer-col {
        display: flex;
        flex-direction: column;         /* 열 내부는 세로 정렬 */
        gap: 10px;                      /* 항목 간 간격 */
        min-width: 180px;               /* 최소 열 너비 */
    }

    .footer-col a {
        color: #42b983;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s;
        padding-left: 4px;              /* 항목 내부 여백 약간 추가 */
    }

    .footer-col a:hover {
        color: #2c8f6e;
    }

    .footer-content {
        text-align: center;
        color: #999;
        font-size: 13px;
        margin-top: 12px;
    }

    .small-btn {
        padding: 6px 10px;
        font-size: 13px;
        margin-left: 8px;
        background-color: #42b983;
        color: #fff;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
    }

    .small-btn:hover {
        background-color: #369f6b;
    }

    .alarm-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .alarm-item {
        padding: 10px 12px;
        border-radius: 8px;
        background-color: #f8f8f8;
        border-left: 4px solid #42b983;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }

    .alarm-item.unread {
        font-weight: bold;
        background-color: #e8f9f2;
    }

    .alarm-message {
        font-size: 14px;
        color: #333;
    }

    .alarm-time {
        margin-top: 4px;
        font-size: 12px;
        color: #888;
    }



</style>
