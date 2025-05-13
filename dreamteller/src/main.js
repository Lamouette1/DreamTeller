import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import './assets/output.css' // Import the compiled Tailwind CSS

createApp(App)
  .use(store)
  .use(router)
  .mount('#app')
