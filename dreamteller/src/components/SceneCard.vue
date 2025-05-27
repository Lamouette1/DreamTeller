<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
    <!-- Scene Image -->
    <div class="relative h-64 bg-gray-200 dark:bg-gray-700">
      <img 
        v-if="scene.imageUrl" 
        :src="scene.imageUrl" 
        :alt="`Scene ${sceneIndex + 1} illustration`" 
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex items-center justify-center">
        <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
      </div>

      <!-- Regenerate Image Button -->
      <button 
        @click="regenerateImage" 
        class="absolute top-2 right-2 bg-white dark:bg-gray-800 p-1 rounded-full shadow-md hover:bg-gray-100 dark:hover:bg-gray-700"
        :disabled="loading"
        title="Regenerate image"
      >
        <svg class="w-5 h-5 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
      </button>
    </div>

    <!-- Scene Text -->
    <div class="p-4">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">Scene {{ sceneIndex + 1 }}</h3>

        <!-- Regenerate Text Button -->
        <button 
          @click="regenerateText" 
          class="bg-gray-100 dark:bg-gray-700 p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 focus:outline-none"
          :disabled="loading"
          title="Regenerate text"
        >
          <svg class="w-5 h-5 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
        </button>
      </div>

      <p class="text-gray-700 dark:text-gray-300">{{ scene.text }}</p>

      <!-- Loading Indicator -->
      <div v-if="loading" class="mt-3 flex justify-center">
        <div class="loader">
          <svg class="animate-spin h-5 w-5 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">Regenerating...</span>
        </div>
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
      loading: false
    }
  },
  methods: {
    async regenerateText() {
      this.loading = true
      try {
        await this.$store.dispatch('regenerateSceneText', this.sceneIndex)
      } catch (error) {
        console.error('Failed to regenerate text:', error)
      } finally {
        this.loading = false
      }
    },
    async regenerateImage() {
      this.loading = true
      try {
        await this.$store.dispatch('regenerateSceneImage', this.sceneIndex)
      } catch (error) {
        console.error('Failed to regenerate image:', error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
