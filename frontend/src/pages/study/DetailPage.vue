<template>
  <div class="detail-page">
    <h1>📌 스터디 상세보기</h1>

    <div class="detail-box">
      <p><strong>스터디명:</strong> {{ study.name }}</p>
      <p><strong>설명:</strong> {{ study.description }}</p>
      <p><strong>리더 ID:</strong> {{ study.leaderId }}</p>
      <p><strong>모집 인원:</strong> {{ study.members }} / {{ study.capacity }}</p>
      <p><strong>시간:</strong> {{ study.time }}</p>
    </div>

    <div class="back-button">
      <button class="list-btn" @click="goToList">← 목록</button>
    </div>

    <div class="action-buttons">
      <button class="edit-btn" @click="goToEdit">✏️ 수정</button>
      <button class="delete-btn" @click="deletePost">🗑️ 삭제</button>
    </div>

    <div class="favorite-box">
      <span class="heart-icon" @click="toggleFavorite">
        {{ isFavorite ? '❤️' : '🤍' }}
      </span>
      <span class="favorite-text">
        {{ isFavorite ? '관심 스터디 등록됨' : '관심 스터디에 추가' }}
      </span>
    </div>

    <button class="join-btn" @click="requestJoin">가입 요청</button>

    <h2>💬 댓글</h2>

    <!-- 댓글 입력 -->
    <input v-model="newComment" placeholder="댓글을 입력하세요" @keyup.enter="addComment" />
    <button @click="addComment">댓글 작성</button>
    </div>

    <!-- 댓글 목록 -->
    <ul class="comment-list">
      <template v-for="comment in topLevelComments" :key="comment.id">
        <li class="comment-item">
          <div class="comment-header">
            <span class="author">{{ comment.author }}</span>
            <span class="timestamp">{{ formatDate(comment.timestamp) }}</span>
          </div>
          <div class="comment-content">{{ comment.content }}</div>
          <div class="comment-actions">
            <button @click="comment.showReply = !comment.showReply">답글</button>
            <button class="delete-btn" @click="deleteComment(comment.id)">삭제</button>
          </div>
          <div v-if="comment.showReply" class="reply-input">
            <input v-model="replyText[comment.id]" placeholder="답글을 입력하세요" />
            <button @click="submitReply(comment.id)">등록</button>
          </div>

          <!-- 대댓글 목록 -->
          <ul class="reply-list">
            <li v-for="reply in repliesFor(comment.id)" :key="reply.id" class="reply-item">
              <div class="comment-header">
                <span class="author">{{ reply.author }}</span>
                <span class="timestamp">{{ formatDate(reply.timestamp) }}</span>
              </div>
              <div class="comment-content">{{ reply.content }}</div>
              <div class="comment-actions">
                <button class="delete-btn" @click="deleteComment(reply.id)">삭제</button>
              </div>
            </li>
          </ul>
        </li>
      </template>
    </ul>

    
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const studyId = route.params.id

const study = ref(null)
const comments = ref([])
const newComment = ref('')
const replyText = ref({})
const isFavorite = ref(false)
const currentUser = 'me123' // 로그인 시스템과 연결 필요

onMounted(async () => {
  try {
    // ✅ 스터디 정보 불러오기
    const studyRes = await axios.get(`/api/studies/${studyId}`)
    study.value = studyRes.data

    // ✅ 댓글 목록 불러오기
    const commentRes = await axios.get(`/api/comments?study_id=${studyId}`)
    comments.value = commentRes.data.map(c => ({ ...c, showReply: false }))
  } catch (err) {
    console.error('데이터 로드 실패:', err)
  }
})

function addComment() {
  const content = newComment.value.trim()
  if (!content) return
  axios.post('/api/comments', {
    study_id: studyId,
    content,
    parent_id: null
  }).then(res => {
    comments.value.push({ ...res.data, showReply: false })
    newComment.value = ''
  })
}

function submitReply(parentId) {
  const content = replyText.value[parentId]?.trim()
  if (!content) return
  axios.post('/api/comments', {
    study_id: studyId,
    content,
    parent_id: parentId
  }).then(res => {
    comments.value.push({ ...res.data, showReply: false })
    replyText.value[parentId] = ''
  })
}

function deleteComment(commentId) {
  axios.delete(`/api/comments/${commentId}`).then(() => {
    comments.value = comments.value.filter(c => c.id !== commentId && c.parent_id !== commentId)
  })
}

function formatDate(ts) {
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  }).format(new Date(ts))
}

const topLevelComments = computed(() => comments.value.filter(c => c.parent_id === null))
function repliesFor(parentId) {
  return comments.value.filter(c => c.parent_id === parentId)
}

function goToList() { router.push('/study/list') }
function goToEdit() { router.push(`/study/${studyId}/edit`) }
function deletePost() {
  if (confirm('정말 삭제하시겠습니까?')) {
    axios.delete(`/api/studies/${studyId}`).then(() => {
      alert('삭제 완료')
      router.push('/study/list')
    })
  }
}
function toggleFavorite() { isFavorite.value = !isFavorite.value }
function requestJoin() { alert('가입 요청이 전송되었습니다!') }
</script>


<style scoped>
.detail-page {
  padding: 20px;
}

.detail-box {
  border: 1px solid #ccc;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.join-btn {
  padding: 10px 16px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  margin-bottom: 24px;
}

.join-btn:hover {
  background-color: #369f6b;
}

.favorite-box {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
}
.heart-icon {
  cursor: pointer;
  font-size: 24px;
  transition: transform 0.2s;
}
.heart-icon:hover {
  transform: scale(1.2);
}
.favorite-text {
  font-size: 16px;
  color: #666;
}

.back-button {
  margin-bottom: 16px;
}
.list-btn {
  background-color: #f0f0f0;
  color: #333;
  border: none;
  padding: 8px 16px;
  font-weight: bold;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.list-btn:hover {
  background-color: #ddd;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin: 8px 0 24px;
}
.edit-btn,
.delete-btn {
  padding: 8px 16px;
  font-size: 14px;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
}
.edit-btn {
  background-color: #42b983;
  color: white;
}
.edit-btn:hover {
  background-color: #369f6b;
}
.delete-btn {
  background-color: #ff5e5e;
  color: white;
}
.delete-btn:hover {
  background-color: #d63030;
}

/* 💬 댓글 스타일 */
.comment-list {
  list-style: none;
  padding: 0;
  margin-bottom: 20px;
}
.comment-item, .reply-item {
  background-color: #f9f9f9;
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 10px;
}
.reply-item {
  margin-left: 24px;
  background-color: #f0f0f0;
}
.comment-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #888;
  margin-bottom: 4px;
}
.comment-content {
  font-size: 14px;
  margin-bottom: 6px;
}
.comment-actions {
  display: flex;
  gap: 8px;
}
.reply-input {
  margin-top: 6px;
}
.reply-input input {
  width: 80%;
  padding: 6px;
  margin-right: 6px;
}
</style>
