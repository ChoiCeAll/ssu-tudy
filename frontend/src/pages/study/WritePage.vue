<template>
  <div class="write-page">
    <h1>{{ isEditMode ? '스터디 수정' : '스터디 등록' }}</h1>

    <form @submit.prevent="handleSubmit">
      <input v-model="form.name" placeholder="스터디명" required />
      <textarea v-model="form.description" placeholder="설명" required />
      <input v-model="form.leaderId" placeholder="리더 ID" required />
      <input v-model="form.hashtags" placeholder="해시태그 (쉼표로 구분)" />

      <select v-model.number="form.capacity" required>
        <option disabled value="">인원 선택</option>
        <option v-for="n in 30" :key="n" :value="n">{{ n }}명</option>
      </select>

      <div class="day-selector">
        <span>요일 선택:</span>
        <div class="day-buttons">
          <button
            v-for="day in days"
            :key="day"
            :class="{ selected: form.day === day }"
            type="button"
            @click="form.day = day"
          >
            {{ day }}
          </button>
        </div>
      </div>

      <label>시간 선택:</label>
      <input type="time" v-model="form.hour" required />

      <button type="submit">{{ isEditMode ? '수정 완료' : '등록하기' }}</button>
    </form>
  </div>
</template>

<script setup>
import { reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const isEditMode = computed(() => !!route.params.id)
const studyId = route.params.id
const days = ['월', '화', '수', '목', '금', '토', '일']

const form = reactive({
  name: '',
  description: '',
  leaderId: '',
  hashtags: '',
  capacity: 5,
  day: '',
  hour: ''
})

onMounted(async () => {
  if (isEditMode.value) {
    const { data } = await axios.get(`/api/studies/${studyId}`)
    form.name = data.name
    form.description = data.description
    form.leaderId = data.leaderId
    form.hashtags = data.hashtags || ''
    form.capacity = data.capacity
    const [day, hour] = data.time.replace('매주 ', '').split(' ')
    form.day = day
    form.hour = hour
  }
})

async function handleSubmit() {
  const timeText = `매주 ${form.day} ${form.hour}`
  const payload = {
    ...form,
    time: timeText
  }

  try {
    if (isEditMode.value) {
      await axios.put(`/api/studies/${studyId}`, payload)
      alert('스터디가 수정되었습니다!')
      router.push(`/study/${studyId}`)
    } else {
      const res = await axios.post('/api/studies', payload)
      alert('스터디가 등록되었습니다!')
      const newId = res.data.id
      router.push(`/study/${newId}`)
    }
  } catch (err) {
    alert('요청 처리 중 오류가 발생했습니다.')
    console.error(err)
  }
}
</script>


<style scoped>
.write-page {
  padding: 20px;
}
form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
input,
textarea,
select {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button {
  padding: 10px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
}
button:hover {
  background-color: #369f6b;
}
.day-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.day-buttons {
  display: flex;
  gap: 8px;
}
.day-buttons button {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background-color: #f5f5f5;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}
.day-buttons button:hover {
  background-color: #e0e0e0;
}
.day-buttons button.selected {
  background-color: #42b983;
  color: white;
  border-color: #42b983;
}
</style>
