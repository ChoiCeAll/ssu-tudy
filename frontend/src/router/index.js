import { createRouter, createWebHistory } from 'vue-router'
import ListPage from '../pages/study/ListPage.vue'

const routes = [
  { path: '/', redirect: '/study/list' },
  { path: '/study/list', component: ListPage }
]

export const router = createRouter({
  history: createWebHistory(),
  routes
})
