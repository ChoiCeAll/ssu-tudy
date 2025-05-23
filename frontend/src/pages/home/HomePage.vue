<template>
  <div class="home-page">
    <h1>🎓 SSU-TUDY 홈</h1>

    <!-- 검색창 + 마스코트 이미지 -->
    <div class="top-section">
      <div class="search-bar">
        <input v-model="searchKeyword" placeholder="스터디명을 검색하세요" @keyup.enter="search" />
        <button @click="search">검색</button>
      </div>
      <img :src="mascotImage" alt="SSU 마스코트" class="mascot-img" />
    </div>

    <!-- 스터디 미리보기 -->
    <section class="preview-section">
      <div class="section-header">
        <h2>📋 최신 스터디</h2>
        <button @click="goToStudyList">전체 보기 →</button>
      </div>
      <ul class="preview-list">
        <li v-for="study in studyPreview" :key="study.id">
          <strong>{{ study.name }}</strong> - {{ study.time }}
        </li>
      </ul>
    </section>

    <!-- 공지사항 미리보기 -->
    <section class="preview-section">
      <div class="section-header">
        <h2>📢 공지사항</h2>
        <button @click="goToNotice">전체 보기 →</button>
      </div>
      <ul class="preview-list">
        <li v-for="notice in notices" :key="notice.id">
          📌 {{ notice.title }}
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import mascotImage from '../../../images/ssu-mascot.png'

const router = useRouter()
const searchKeyword = ref('')

// 임시 데이터
const studyPreview = ref([
  { id: 1, name: 'Vue 스터디', time: '월 19:00' },
  { id: 2, name: 'CS 면접', time: '수 21:00' },
  { id: 3, name: '알고리즘', time: '토 10:00' }
])

const notices = ref([
  { id: 1, title: '스터디 개설 기능 오픈 안내' },
  { id: 2, title: '신규 기능 업데이트 안내' }
])

function search() {
  router.push({ path: '/study/list', query: { q: searchKeyword.value } })
}

function goToStudyList() {
  router.push('/study/list')
}

function goToNotice() {
  router.push('/notice')
}
</script>

<style scoped>
.home-page {
  padding: 24px;
}

/* 상단 검색창 + 이미지 */
.top-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}

.search-bar {
  display: flex;
  flex: 1;
  gap: 8px;
}
.search-bar input {
  flex: 1;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
}
.search-bar button {
  padding: 10px 16px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* 마스코트 이미지 */
.mascot-img {
  width: 120px;
  height: auto;
  object-fit: contain;
}

.preview-section {
  margin-bottom: 32px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.preview-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.preview-list li {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}
</style>
