<template>
  <div>
    <div v-if="story" class="space-y-8">
      <!-- Story Header -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">{{ story.title }}</h1>
        <p class="text-gray-600 dark:text-gray-400">{{ storyDetails }}</p>
        
        <!-- Export Options -->
        <div class="mt-4 flex space-x-3">
          <button 
            @click="exportToPDF" 
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
            </svg>
            Export as PDF
          </button>
          <button 
            @click="copyShareLink" 
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"></path>
            </svg>
            Copy Share Link
          </button>
        </div>
      </div>
      
      <!-- Scene Cards -->
      <div class="grid grid-cols-1 gap-6">
        <scene-card
          v-for="(scene, index) in story.scenes"
          :key="index"
          :scene="scene"
          :scene-index="index"
        />
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-else-if="loading" class="flex justify-center items-center h-64">
      <div class="loader flex items-center">
        <svg class="animate-spin h-8 w-8 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="ml-3 text-lg text-gray-600 dark:text-gray-400">Loading your story...</span>
      </div>
    </div>
    
    <!-- Error State -->
    <div v-else class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 text-center">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <h3 class="mt-2 text-lg font-medium text-gray-900 dark:text-white">Story not found</h3>
      <p class="mt-1 text-gray-500 dark:text-gray-400">The story you're looking for doesn't exist or is still being generated.</p>
      <div class="mt-6">
        <router-link to="/create" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          Create a New Story
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import SceneCard from '@/components/SceneCard.vue'
import html2pdf from 'html2pdf.js'

export default {
  name: 'StoryViewer',
  components: {
    SceneCard
  },
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      shareUrl: '',
      showShareMessage: false
    }
  },
  computed: {
    story() {
      return this.$store.getters.getStoryById(this.id) || this.$store.state.currentStory
    },
    storyDetails() {
      if (!this.story) return ''
      return `A ${this.story.prompt.genre.toLowerCase()} story with a ${this.story.prompt.tone.toLowerCase()} tone, illustrated in ${this.story.prompt.artStyle.toLowerCase()} style.`
    }
  },
  created() {
    this.loading = true
    // If story is not in the store, we could fetch it from an API
    // For now, we'll just set loading to false after a short delay
    setTimeout(() => {
      this.loading = false
    }, 1000)
  },
  methods: {
    exportToPDF() {
      const element = document.createElement('div')
      element.innerHTML = `
        <h1 style="font-size: 24px; margin-bottom: 10px;">${this.story.title}</h1>
        <p style="font-size: 14px; color: #666; margin-bottom: 30px;">${this.storyDetails}</p>
        ${this.story.scenes.map((scene, index) => `
          <div style="margin-bottom: 30px;">
            <h2 style="font-size: 18px; margin-bottom: 10px;">Scene ${index + 1}</h2>
            <img src="${scene.imageUrl}" style="width: 100%; height: auto; margin-bottom: 10px;" />
            <p>${scene.text}</p>
          </div>
        `).join('')}
      `
      
      const opt = {
        margin: 1,
        filename: `${this.story.title.replace(/\s+/g, '_')}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
      }
      
      html2pdf().set(opt).from(element).save()
    },
    copyShareLink() {
      // In a real app, this would create a unique URL for sharing
      const shareableUrl = `${window.location.origin}/story/${this.id}`
      navigator.clipboard.writeText(shareableUrl)
        .then(() => {
          this.shareUrl = shareableUrl
          this.showShareMessage = true
          setTimeout(() => {
            this.showShareMessage = false
          }, 3000)
        })
        .catch(err => {
          console.error('Failed to copy URL: ', err)
        })
    }
  }
}
</script>
