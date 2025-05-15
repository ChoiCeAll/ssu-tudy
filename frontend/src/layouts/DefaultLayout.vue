<template>
    <div class="layout">
        <header class="header">
            <div class="logo">SSU-TUDY</div>
            <div class="header-right">
                <span v-if="!state.isLoggedIn" @click="openLoginModal" class="clickable">로그인</span>
                <span v-else>
                    <span class="icon clickable" @click="togglePanel('alarm')">🔔</span>
                    <span class="icon clickable" @click="togglePanel('chat')">💬</span>
                    <span class="icon clickable" @click="togglePanel('profile')">👤</span>
                </span>
            </div>
        </header>

        <main class="main">
            <slot />
        </main>

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
                        <ul>
                            <li v-for="alarm in state.alarms" :key="alarm.id">{{ alarm.message }}</li>
                        </ul>
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
                            <input v-if="state.editMode" v-model="state.profile.nickname" />
                            <span v-else>{{ state.profile.nickname }}</span>
                        </div>
                    </div>

                    <div class="profile-item">
                        <label>학번</label>
                        <div class="field">
                            <input v-if="state.editMode" v-model="state.profile.studentId" />
                            <span v-else>{{ state.profile.studentId }}</span>
                        </div>
                    </div>

                    <div class="profile-item">
                        <label>전공</label>
                        <div class="field">
                            <input v-if="state.editMode" v-model="state.profile.major" />
                            <span v-else>{{ state.profile.major }}</span>
                        </div>
                    </div>

                    <div class="profile-item">
                        <label>알림 해시태그</label>
                        <div class="hashtags">
                            <div v-for="(tag, index) in state.hashtags" :key="index" class="tag-input">
                                <input v-if="state.editMode" v-model="state.hashtags[index]" />
                                <span v-else>{{ state.hashtags[index] }}</span>
                            </div>
                            <button @click="addHashtag">+ 해시태그 추가</button>
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
                <p>계정이 없으신가요? <a href="/register">회원가입</a></p>
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

const chatPopupRef = ref(null)
const chatHeaderRef = ref(null)

const state = reactive({
    isLoggedIn: false,
    showLogin: false,
    userName: '',
    id: '',
    pw: '',
    showPanel: false,
    panelType: '', // 'alarm' 'chat' 'profile'
    alarms: [],
    profile: {
        nickname: 'choi123',
        studentId: '20231234',
        major: 'AI융합학과'
    },
    editMode: false,
    hashtags: ['#성실함', '#프론트엔드'],
    originProfile: {
        nickname: '',
        studentId: '',
        major: ''
    },
    originHashtags: [],

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
    userId : 1
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

// 마우스오버 시 보여줄 툴팁
const getProfileTooltip = (id) => {
    const user = userMap[id]
    return user ? `${user.nickname} (${user.studentId})` : '알 수 없음'

}

onMounted(() => {
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
function login() {
    var logid = state.id.trim()
    var logpw = state.pw.trim()
    if (logid != '' && logpw != '') {
        state.userName = logid
        state.isLoggedIn = true
        state.showLogin = false
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
        }
    }
}

function toggleEdit() {
    state.originProfile = JSON.parse(JSON.stringify(state.profile))
    state.originHashtags = [...state.hashtags]
    state.editMode = true
}

function cancelEdit() {
    state.profile = JSON.parse(JSON.stringify(state.originProfile))
    state.hashtags = [...state.originHashtags]

    state.originProfile = {
        nickname: '',
        studentId: '',
        major: ''
    }
    state.originHashtags = []
    state.editMode = false
}

function saveEdit() {
    // 실제 저장 로직은 여기에 추가 (예: API 호출)
    state.editMode = false
}
function addHashtag() {
    state.hashtags.push('#')
}

async function fetchAlarms() {
    try {
        const res = await fetch('/api/alarms')  // 예시
        const data = await res.json()
        state.alarms = data
    } catch (e) {
        console.error('알람 불러오기 실패:', e)
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

</script>

<style>
    
    *:not(input):not(textarea) {
        caret-color: transparent;
    }
    .layout {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 24px;
        background-color: #fff;
        border-bottom: 1px solid #ddd;
    }
    .logo {
        font-weight: bold;
        font-size: 20px;
        color: #42b983;
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
    .main {
        padding: 20px;
        flex: 1;
        overflow-y: auto;
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
        gap: 8px;
        margin-top: 24px;
    }

    .edit-buttons button {
        padding: 6px 12px;
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




</style>
