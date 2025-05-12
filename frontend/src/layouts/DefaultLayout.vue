<template>
    <div class="layout">
        <header class="header">
            <div class="logo">SSU-TUDY</div>
            <div class="header-right">
                <span v-if="!state.isLoggedIn" @click="openLoginModal" class="clickable">로그인</span>
                <span v-else class="username">{{ state.userName }}</span>
                <span class="icon">🔔</span>
                <span class="icon">👤</span>
            </div>
        </header>

        <main class="main">
            <slot />
        </main>

        <!-- 로그인 모달 -->
        <div v-if="state.showLogin" class="modal">
            <div class="modal-content">
                <button class="close-btn" @click="state.showLogin = false">❌</button>
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
    </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const state = reactive({
    isLoggedIn: false,
    showLogin: false,
    userName: '',
    id: '',
    pw: ''
})

function openLoginModal() {
    state.showLogin = true
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
</script>

<style scoped>
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
.username {
    font-weight: 500;
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
</style>
