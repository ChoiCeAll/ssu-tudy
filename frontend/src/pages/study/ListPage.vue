<template>
    <div class="list-page">
        <h1>📋 스터디 목록</h1>

        <!-- 🔍 검색창 -->
        <div class="search-bar">
            <input type="text" v-model="searchKeyword" placeholder="스터디명을 검색하세요" @keyup.enter="search" />
            <button @click="search">검색</button>
        </div>

        <!-- 📄 스터디 리스트 테이블 -->
        <table class="study-table">
            <thead>
                <tr>
                    <th>번호</th>
                    <th>스터디명</th>
                    <th>설명</th>
                    <th>리더 ID</th>
                    <th>모집 인원</th>
                    <th>시간</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(study, idx) in filteredList" :key="study.id">
                    <td>{{ filteredList.length - idx }}</td>
                    <td>{{ study.name }}</td>
                    <td>{{ study.description }}</td>
                    <td>{{ study.leaderId }}</td>
                    <td>{{ study.members }}/{{ study.capacity }}</td>
                    <td>{{ study.time }}</td>
                </tr>
                <tr v-if="filteredList.length === 0">
                    <td colspan="6" class="empty">검색 결과가 없습니다.</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup>
import { reactive, computed } from 'vue'

const state = reactive({
    searchKeyword: '',
    studyList: [
        { id: 1, name: 'Vue 기초', description: 'Vue 3 학습 스터디', leaderId: 'choi123', members: 4, capacity: 6, time: '매주 월 19:00' },
        { id: 2, name: 'CS 면접 대비', description: '컴공 전공자 모임', leaderId: 'lee456', members: 5, capacity: 5, time: '매주 수 21:00' },
        { id: 3, name: '알고리즘', description: '백준 레벨업', leaderId: 'kim789', members: 2, capacity: 5, time: '매주 토 10:00' }
        // TODO: 실제 데이터로 대체
    ]
})

const filteredList = computed(() => {
    if (!state.searchKeyword) return [...state.studyList].reverse()
    return [...state.studyList]
        .filter(s => s.name.includes(state.searchKeyword))
        .reverse()
})

function search() {
    // 추가 로직이 있다면 이곳에 삽입
}
</script>

<style scoped>
.list-page {
    padding: 20px;
}
.search-bar {
    margin-bottom: 16px;
    display: flex;
    gap: 8px;
}
.search-bar input {
    flex: 1;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}
.search-bar button {
    padding: 8px 12px;
    background-color: #42b983;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
.search-bar button:hover {
    background-color: #369f6b;
}
.study-table {
    width: 100%;
    border-collapse: collapse;
    user-select: none; /* 테이블 전체 선택 방지 */
}
.study-table th,
.study-table td {
    padding: 10px;
    border: 1px solid #ccc;
    text-align: center;
    user-select: none; /* 텍스트 선택 방지 */
    cursor: default;   /* 마우스 커서 기본 화살표로 고정 */
    outline: none;        /* ✅ 포커스 테두리 제거 */
    caret-color: transparent;
}
.study-table th {
    background-color: #f9f9f9;
}
.empty {
    text-align: center;
    color: #aaa;
    padding: 20px;
}
</style>
