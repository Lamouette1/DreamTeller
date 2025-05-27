<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
    <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Export & Share</h2>

    <div class="space-y-4">
      <!-- Export as PDF -->
      <div>
        <button 
          @click="exportToPDF" 
          class="w-full flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
          </svg>
          Download as PDF
        </button>
      </div>

      <!-- Share Link -->
      <div>
        <button 
          @click="generateShareLink" 
          class="w-full flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"></path>
          </svg>
          Generate Share Link
        </button>
      </div>

      <!-- Share Link Display (when available) -->
      <div v-if="shareUrl" class="mt-4">
        <label for="share-url" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Share URL</label>
        <div class="mt-1 flex rounded-md shadow-sm">
          <input 
            id="share-url" 
            type="text" 
            readonly 
            :value="shareUrl" 
            class="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-l-md border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
          />
          <button 
            @click="copyToClipboard" 
            class="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 dark:border-gray-600 rounded-r-md bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-300 sm:text-sm"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path>
            </svg>
          </button>
        </div>
        <p v-if="copied" class="mt-2 text-sm text-green-600 dark:text-green-400">Copied to clipboard!</p>
      </div>
    </div>
  </div>
</template>

<script>
import html2pdf from 'html2pdf.js'

export default {
  name: 'ExportOptions',
  props: {
    story: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      shareUrl: '',
      copied: false
    }
  },
  methods: {
    exportToPDF() {
      // Similar to the method in StoryViewer
      const element = document.createElement('div')
      element.innerHTML = `
        <h1 style="font-size: 24px; margin-bottom: 10px;">${this.story.title}</h1>
        <p style="font-size: 14px; color: #666; margin-bottom: 30px;">
          A ${this.story.prompt.genre.toLowerCase()} story with a ${this.story.prompt.tone.toLowerCase()} tone.
        </p>
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

    generateShareLink() {
      // In a real app, this would create a unique URL for sharing
      // For demo purposes, we'll just use the story ID in the URL
      this.shareUrl = `${window.location.origin}/story/${this.story.id}`
    },

    copyToClipboard() {
      navigator.clipboard.writeText(this.shareUrl)
        .then(() => {
          this.copied = true
          setTimeout(() => {
            this.copied = false
          }, 3000)
        })
        .catch(err => {
          console.error('Failed to copy text: ', err)
        })
    }
  }
}
</script>