// main.js
import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router'         // ✅ 이 줄 추가 (경로는 실제 위치에 맞게)
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

const app = createApp(App)

app.use(router)                            // ✅ 라우터 등록
app.use(Toast)
app.mount('#app')
