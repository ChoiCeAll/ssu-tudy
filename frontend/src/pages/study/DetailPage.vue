<template>
  <div class="detail-page">
    <h1>📌 스터디 상세보기</h1>

    <div class="detail-box" v-if="study">
      <img :src="study.image" class="detail-img" />
      <p><strong>스터디명:</strong> {{ study.name }}</p>
      <p><strong>해시태그:</strong> {{ formattedHashtags }}</p>
      <p><strong>리더 ID:</strong> {{ study.leaderLoginId }}</p>
      <p><strong>모집 인원:</strong> {{ study.members }} / {{ study.capacity }}</p>
      <p><strong>시간:</strong> {{ study.time }}</p>
    </div>

    <div class="back-button">
      <button class="list-btn" @click="goToList">목록으로</button>
    </div>

    <div class="action-buttons" v-if="isAuthor">
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

    <input v-model="newComment" placeholder="댓글을 입력하세요" @keyup.enter="addComment" />
    <button @click="addComment">댓글 작성</button>

    <ul class="comment-list">
      <template v-for="comment in topLevelComments" :key="comment.id">
        <li class="comment-item">
          <div class="comment-header">
            <span class="author">{{ comment.author }}</span>
            <span class="timestamp">{{ formatDate(comment.created_at) }}</span>
          </div>
          <div class="comment-content">
            <input v-if="editId === comment.id" v-model="editText" />
            <span v-else>{{ comment.content }}</span>
          </div>
          <div class="comment-actions">
            <button @click="comment.showReply = !comment.showReply">답글</button>
            <template v-if="comment.author_id === sessionUserId">
              <button @click="startEdit(comment)">수정</button>
              <button v-if="editId === comment.id" @click="submitEdit(comment.id)">수정 완료</button>
              <button @click="confirmDelete(comment.id)">삭제</button>
            </template>
          </div>
          <div v-if="comment.showReply" class="reply-input">
            <input v-model="replyText[comment.id]" placeholder="답글을 입력하세요" />
            <button @click="submitReply(comment.id)">등록</button>
          </div>

          <ul class="reply-list">
            <li v-for="reply in repliesFor(comment.id)" :key="reply.id" class="reply-wrapper">
              <div class="reply-thread">ㄴ</div>
              <div class="reply-item">
                <div class="comment-header">
                  <span class="author">{{ reply.author }}</span>
                  <span class="timestamp">{{ formatDate(reply.created_at) }}</span>
                </div>
                <div class="comment-content">
                  <input v-if="editId === reply.id" v-model="editText" />
                  <span v-else>{{ reply.content }}</span>
                </div>
                <div class="comment-actions" v-if="reply.author_id === sessionUserId">
                  <button @click="startEdit(reply)">수정</button>
                  <button v-if="editId === reply.id" @click="submitEdit(reply.id)">수정 완료</button>
                  <button @click="confirmDelete(reply.id)">삭제</button>
                </div>
              </div>
            </li>
          </ul>
        </li>
      </template>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { useToast } from 'vue-toastification'

const toast = useToast()
const router = useRouter()
const route = useRoute()

const sessionUserId = ref(null)
const study = ref(null)
const comments = ref([])
const newComment = ref('')
const replyText = ref({})
const isFavorite = ref(false)
const editId = ref(null)
const editText = ref('')
const defaultImage = '../../../images/default_study.png'

const isAuthor = computed(() => study.value && study.value.leaderId === sessionUserId.value)
const formattedHashtags = computed(() =>
  study.value?.hashtags ? '#' + study.value.hashtags.split(',').join(' #') : ''
)

async function fetchStudyDetail(id) {
  try {
    const session = await axios.get('/api/session-check')
    if (session.data.is_logged_in) sessionUserId.value = session.data.user_id

    const res = await axios.get(`/api/studies/${id}`)
    const data = res.data

    data.image = (!data.image || data.image.trim() === '') ? defaultImage : data.image
    study.value = data
    isFavorite.value = data.is_favorited

    const commentRes = await axios.get(`/api/comments?study_id=${id}`)
    comments.value = commentRes.data.map(c => ({ ...c, showReply: false }))
  } catch (err) {
    console.error('상세 정보 로드 실패:', err)
  }
}

onMounted(() => {
  fetchStudyDetail(route.params.id)
})

watch(() => route.params.id, (newId) => {
  fetchStudyDetail(newId)
})

function addComment() {
  const content = newComment.value.trim()
  if (!content) return
  axios.post('/api/comments', {
    study_id: route.params.id,
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
    study_id: route.params.id,
    content,
    parent_id: parentId
  }).then(res => {
    comments.value.push({ ...res.data, showReply: false })
    replyText.value[parentId] = ''
  })
}

function confirmDelete(commentId) {
  if (confirm('댓글을 삭제하시겠습니까?')) {
    deleteComment(commentId)
  }
}

function deleteComment(commentId) {
  comments.value = comments.value.filter(c => c.id !== commentId && c.parent_id !== commentId)
  axios.delete(`/api/comments/${commentId}`)
}

function startEdit(comment) {
  editId.value = comment.id
  editText.value = comment.content
}

function submitEdit(commentId) {
  const content = editText.value.trim()
  if (!content) return
  axios.put(`/api/comments/${commentId}`, { content }).then(() => {
    const comment = comments.value.find(c => c.id === commentId)
    if (comment) comment.content = content
    editId.value = null
    editText.value = ''
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

function goToList() {
  router.push('/study/list')
}

function goToEdit() {
  router.push(`/study/${route.params.id}/edit`)
}

function deletePost() {
  if (confirm('정말 삭제하시겠습니까?')) {
    axios.delete(`/api/studies/${route.params.id}`)
      .then(() => {
        toast.success('삭제 완료')
        router.push('/study/list')
      })
      .catch(() => {
        toast.error('삭제 중 오류가 발생했습니다')
      })
  }
}

function toggleFavorite() {
  const url = isFavorite.value
    ? `/api/study/${route.params.id}/unfavorite`
    : `/api/study/${route.params.id}/favorite`

  axios.post(url)
    .then(res => {
      toast.success(res.data.message)
      isFavorite.value = !isFavorite.value
    })
    .catch(err => {
      const msg = err.response?.data?.error || '요청 실패'
      toast.error(`⚠ ${msg}`)
    })
}

function requestJoin() {
  axios.post(`/api/study/${route.params.id}/apply`)
    .then(res => {
      toast.success(res.data.message || '스터디 신청 완료')
    })
    .catch(err => {
      const msg = err.response?.data?.error || '신청 실패'
      toast.error(`⚠ ${msg}`)
    })
}
</script>

<style scoped>
.detail-page {
  padding: 20px;
}
.detail-img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin-bottom: 16px;
}
.detail-box {
  border: 1px solid #ccc;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.join-btn {
  margin-bottom: 24px;
  padding: 10px 16px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
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
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: bold;
  border: none;
  cursor: pointer;
}
</style>
