// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import CreateStory from '../views/CreateStory.vue'
import ViewStory from '../views/ViewStory.vue'
import About from '../views/About.vue'
import LoadStory from '../views/LoadStory.vue' // Add import for LoadStory

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/create',
    name: 'CreateStory',
    component: CreateStory
  },
  {
    path: '/story/:id',
    name: 'ViewStory',
    component: ViewStory,
    props: true
  },
  {
    path: '/about',
    name: 'About',
    component: About
  },
  {
    path: '/load',
    name: 'LoadStory',
    component: LoadStory
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router