import { createRouter, createWebHistory } from 'vue-router'
import ListPage from '../pages/study/ListPage.vue'
import HomePage from '../pages/home/HomePage.vue'
import DetailPage from '../pages/study/DetailPage.vue'
import WritePage from '../pages/study/WritePage.vue'

const routes = [
  { path: '/', redirect: '/study/list' },
  { path: '/study/list', component: ListPage },
  { path: '/study/:id', component: DetailPage }, //상세페이지
  { path: '/study/write', component: WritePage },      // 등록
  { path: '/study/:id/edit', component: WritePage }    // 수정
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})
