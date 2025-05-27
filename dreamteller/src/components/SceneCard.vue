// src/components/SceneCard.vue
<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
    <!-- Scene Image -->
    <div class="relative bg-gray-200 dark:bg-gray-700">
      <!-- Image container with proper aspect ratio -->
      <div v-if="scene.imageUrl" class="relative w-full" style="height: 650px;">
        <img 
          :src="scene.imageUrl" 
          :alt="`Scene ${sceneIndex + 1} illustration`" 
          class="w-full h-auto object-contain bg-gray-100 dark:bg-gray-800"
          @load="onImageLoad"
          @error="onImageError"
        />
        
        <!-- Loading overlay while image loads -->
        <div v-if="imageLoading" class="absolute inset-0 flex items-center justify-center bg-gray-200 dark:bg-gray-700">
          <svg class="animate-spin h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      </div>
      
      <!-- Placeholder when no image -->
      <div v-else class="w-full h-64 flex items-center justify-center">
        <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
      </div>

      <!-- Regenerate Image Button -->
      <button 
        @click="regenerateImage" 
        class="absolute top-2 right-2 bg-white dark:bg-gray-800 p-2 rounded-full shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200 z-10"
        :disabled="loading"
        title="Regenerate image"
      >
        <svg 
          class="w-5 h-5 text-gray-700 dark:text-gray-300" 
          :class="{ 'animate-spin': loading }" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24" 
          xmlns="http://www.w3.org/2000/svg"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
      </button>

      <!-- Image error state -->
      <div v-if="imageError" class="absolute inset-0 flex items-center justify-center bg-red-50 dark:bg-red-900/20">
        <div class="text-center p-4">
          <svg class="w-8 h-8 text-red-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p class="text-sm text-red-600 dark:text-red-400">Failed to load image</p>
          <button 
            @click="retryImageLoad" 
            class="mt-2 text-xs text-red-500 hover:text-red-700 underline"
          >
            Retry
          </button>
        </div>
      </div>
    </div>

    <!-- Scene Text -->
    <div class="p-6">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-white">Scene {{ sceneIndex + 1 }}</h3>

        <!-- Regenerate Text Button -->
        <button 
          @click="regenerateText" 
          class="bg-gray-100 dark:bg-gray-700 p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors duration-200"
          :disabled="loading"
          title="Regenerate text"
        >
          <svg 
            class="w-5 h-5 text-gray-700 dark:text-gray-300" 
            :class="{ 'animate-spin': loading }" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24" 
            xmlns="http://www.w3.org/2000/svg"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
        </button>
      </div>

      <div class="prose prose-gray dark:prose-invert max-w-none">
        <p class="text-gray-700 dark:text-gray-300 leading-relaxed">{{ scene.text }}</p>
      </div>

      <!-- Loading Indicator -->
      <div v-if="loading" class="mt-4 flex items-center justify-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <svg class="animate-spin h-5 w-5 text-indigo-500 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-sm text-gray-600 dark:text-gray-400">
          {{ loadingMessage }}
        </span>
      </div>

      <!-- Success/Error messages -->
      <div v-if="message" class="mt-4 p-3 rounded-lg" :class="messageClass">
        <p class="text-sm" :class="messageTextClass">{{ message }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SceneCard',
  props: {
    scene: {
      type: Object,
      required: true
    },
    sceneIndex: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      imageLoading: true,
      imageError: false,
      loadingMessage: '',
      message: '',
      messageType: ''
    }
  },
  computed: {
    messageClass() {
      return {
        'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800': this.messageType === 'success',
        'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800': this.messageType === 'error',
        'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800': this.messageType === 'info'
      }
    },
    messageTextClass() {
      return {
        'text-green-800 dark:text-green-300': this.messageType === 'success',
        'text-red-800 dark:text-red-300': this.messageType === 'error',
        'text-blue-800 dark:text-blue-300': this.messageType === 'info'
      }
    }
  },
  methods: {
    async regenerateText() {
      this.loading = true
      this.loadingMessage = 'Regenerating scene text...'
      this.message = ''
      
      try {
        await this.$store.dispatch('regenerateSceneText', this.sceneIndex)
        this.showMessage('Scene text regenerated successfully!', 'success')
      } catch (error) {
        console.error('Failed to regenerate text:', error)
        this.showMessage('Failed to regenerate text. Please try again.', 'error')
      } finally {
        this.loading = false
        this.loadingMessage = ''
      }
    },

    async regenerateImage() {
      this.loading = true
      this.loadingMessage = 'Regenerating scene image...'
      this.message = ''
      
      try {
        await this.$store.dispatch('regenerateSceneImage', this.sceneIndex)
        this.showMessage('Scene image regenerated successfully!', 'success')
      } catch (error) {
        console.error('Failed to regenerate image:', error)
        this.showMessage('Failed to regenerate image. Please try again.', 'error')
      } finally {
        this.loading = false
        this.loadingMessage = ''
      }
    },

    onImageLoad() {
      this.imageLoading = false
      this.imageError = false
    },

    onImageError() {
      this.imageLoading = false
      this.imageError = true
    },

    retryImageLoad() {
      this.imageError = false
      this.imageLoading = true
      // Force image reload by adding a timestamp
      const img = this.$el.querySelector('img')
      if (img && this.scene.imageUrl) {
        const originalSrc = this.scene.imageUrl
        img.src = originalSrc + (originalSrc.includes('?') ? '&' : '?') + 'retry=' + Date.now()
      }
    },

    showMessage(text, type) {
      this.message = text
      this.messageType = type
      
      // Auto-hide message after 5 seconds
      setTimeout(() => {
        this.message = ''
        this.messageType = ''
      }, 5000)
    }
  },

  mounted() {
    // If image is already loaded, set imageLoading to false
    if (this.scene.imageUrl) {
      const img = new Image()
      img.onload = () => {
        this.imageLoading = false
      }
      img.onerror = () => {
        this.imageLoading = false
        this.imageError = true
      }
      img.src = this.scene.imageUrl
    } else {
      this.imageLoading = false
    }
  }
}
</script>

<style scoped>
/* Ensure images maintain their aspect ratio */
img {
  max-height: 70vh; /* Prevent extremely tall images */
  min-height: 200px; /* Ensure minimum size for very small images */
}

/* Smooth transitions */
.transition-colors {
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* Loading animation */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Hover effects */
button:hover:not(:disabled) {
  transform: translateY(-1px);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
</style>