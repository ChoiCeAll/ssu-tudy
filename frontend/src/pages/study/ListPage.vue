<template>
  <div class="list-page">
    <h1>📋 스터디 목록</h1>

    <!-- 🔍 검색창 -->
    <div class="search-bar">
      <input
        type="text"
        v-model="searchKeyword"
        placeholder="스터디명을 검색하세요"
        @keyup.enter="search"
      />
      <button @click="search">검색</button>
    </div>

    <!-- 🎯 Masonry 카드 목록 -->
    <div class="masonry-row">
      <div class="masonry-column" v-for="(column, cIdx) in columnList" :key="cIdx">
        <div v-for="study in column" :key="study.id" class="study-card">
          <img :src="study.image" alt="스터디 이미지" class="study-img" />
          <h3 class="study-title" @click="goToDetail(study.id)">{{ study.name }}</h3>
          <p class="study-desc">{{ study.description }}</p>
          <p class="study-meta">👤 {{ study.leaderId }} | 👥 {{ study.members }}/{{ study.capacity }}</p>
          <p class="study-meta">⏰ {{ study.time }}</p>
        </div>
      </div>
    </div>

    <div v-if="paginatedList.length === 0" class="empty">검색 결과가 없습니다.</div>

    <!-- 페이지네이션 -->
    <nav class="pagination">
      <button :disabled="currentPage === 1" @click="currentPage--">←</button>
      <button
        v-for="p in totalPages"
        :key="p"
        :class="{ active: p === currentPage }"
        @click="goToPage(p)"
      >
        {{ p }}
      </button>
      <button :disabled="currentPage === totalPages" @click="currentPage++">→</button>
    </nav>

    <!-- ➕ 등록 버튼 -->
    <button class="write-button" @click="goToWrite">➕ 스터디 등록</button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const searchKeyword = ref('')
const studyList = ref([])
const currentPage = ref(1)
const pageSize = 6
const defaultImage = '/default.jpg'

function goToWrite() {
  router.push('/study/write')
}

function goToDetail(id) {
  router.push(`/study/${id}`)
}

async function fetchStudies() {
  try {
    const res = await axios.get('/api/studies', {
      params: { query: searchKeyword.value }
    })
    studyList.value = res.data.map((item) => ({
      ...item,
      image: item.image || defaultImage
    }))
  } catch (err) {
    console.error('스터디 목록 불러오기 실패', err)
  }
}

function search() {
  currentPage.value = 1
  fetchStudies()
}

function goToPage(p) {
  if (p >= 1 && p <= totalPages.value) {
    currentPage.value = p
  }
}

const totalPages = computed(() => Math.ceil(studyList.value.length / pageSize))

const paginatedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return studyList.value.slice(start, end)
})

const columnList = computed(() => {
  const result = [[], [], []]
  paginatedList.value.forEach((item, idx) => {
    result[idx % 3].push(item)
  })
  return result
})

onMounted(() => {
  fetchStudies()
})
</script>

<style scoped>
.list-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
.search-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
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
.masonry-row {
  display: flex;
  gap: 24px;
}
.masonry-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.study-card {
  background: white;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}
.study-card:hover {
  transform: translateY(-4px);
}
.study-img {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 12px;
  object-fit: cover;
}
.study-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #42b983;
  cursor: pointer;
}
.study-desc {
  color: #555;
  font-size: 14px;
  margin-bottom: 12px;
}
.study-meta {
  font-size: 12px;
  color: #777;
  line-height: 1.4;
}
.empty {
  text-align: center;
  color: #aaa;
  padding: 40px;
}
.write-button {
  position: fixed;
  bottom: 32px;
  right: 32px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 50px;
  padding: 12px 20px;
  font-size: 16px;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  z-index: 100;
  transition: background-color 0.2s;
}
.write-button:hover {
  background-color: #369f6b;
}
.pagination {
  margin-top: 32px;
  text-align: center;
}
.pagination button {
  margin: 0 4px;
  padding: 6px 12px;
  border: 1px solid #ccc;
  background-color: white;
  cursor: pointer;
  border-radius: 4px;
}
.pagination button.active {
  background-color: #42b983;
  color: white;
  font-weight: bold;
}
.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
