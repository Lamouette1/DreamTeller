// src/components/LoadStory.vue
<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Load Saved Stories</h2>

    <!-- Upload Story Section -->
    <div class="mb-8 p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3">Upload Story File</h3>
      <input
        type="file"
        @change="handleFileUpload"
        accept=".story"
        ref="fileInput"
        class="hidden"
      />
      <button
        @click="$refs.fileInput.click()"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        :disabled="uploading"
      >
        <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
        </svg>
        {{ uploading ? 'Uploading...' : 'Choose .story File' }}
      </button>
      <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
        Upload a previously saved .story file
      </p>
    </div>

    <!-- Saved Stories List -->
    <div>
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">Saved Stories</h3>
        <button
          @click="refreshList"
          class="inline-flex items-center px-3 py-1 border border-gray-300 dark:border-gray-600 text-sm rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
          :disabled="loading"
        >
          <svg class="h-4 w-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          <span class="ml-2">Refresh</span>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-8">
        <svg class="animate-spin h-8 w-8 text-indigo-500 mx-auto" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-2 text-gray-500 dark:text-gray-400">Loading saved stories...</p>
      </div>

      <!-- Stories Grid -->
      <div v-else-if="savedStories.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="story in savedStories"
          :key="story.filename"
          class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-lg transition-shadow"
        >
          <h4 class="font-medium text-gray-900 dark:text-white mb-2">{{ story.title }}</h4>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">
            {{ story.num_scenes }} scenes • {{ formatDate(story.creation_date) }}
          </p>
          <p class="text-sm text-gray-600 dark:text-gray-300 mb-3">
            {{ story.prompt.genre }} • {{ story.prompt.tone }}
          </p>
          <div class="flex space-x-2">
            <button
              @click="loadStory(story.filename)"
              class="flex-1 px-3 py-1 text-sm border border-transparent rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              :disabled="loadingStory === story.filename"
            >
              {{ loadingStory === story.filename ? 'Loading...' : 'Load' }}
            </button>
            <button
              @click="downloadStory(story.filename)"
              class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
              </svg>
            </button>
            <button
              @click="deleteStory(story.filename)"
              class="px-3 py-1 text-sm border border-red-300 dark:border-red-700 rounded-md text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-8">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
        </svg>
        <p class="mt-2 text-gray-500 dark:text-gray-400">No saved stories found</p>
      </div>
    </div>

    <!-- Status Messages -->
    <div v-if="statusMessage" class="mt-4">
      <div
        class="rounded-md p-4"
        :class="{
          'bg-green-50 dark:bg-green-900/20': statusType === 'success',
          'bg-red-50 dark:bg-red-900/20': statusType === 'error'
        }"
      >
        <p
          class="text-sm"
          :class="{
            'text-green-800 dark:text-green-300': statusType === 'success',
            'text-red-800 dark:text-red-300': statusType === 'error'
          }"
        >
          {{ statusMessage }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import storyService from '@/services/storyService'

export default {
  name: 'LoadStory',
  data() {
    return {
      savedStories: [],
      loading: false,
      uploading: false,
      loadingStory: null,
      statusMessage: '',
      statusType: ''
    }
  },
  created() {
    this.fetchSavedStories()
  },
  methods: {
    // In LoadStory.vue - fetchSavedStories method
    async fetchSavedStories() {
      this.loading = true;
      this.statusMessage = '';
      this.statusType = '';

      try {
        const response = await storyService.listSavedStories();
        this.savedStories = response.stories || [];

        console.log(`Found ${this.savedStories.length} saved stories`);

        // If no stories found, display a helpful message
        if (this.savedStories.length === 0) {
          this.statusMessage = 'No saved stories found. Try creating and saving a new story first.';
          this.statusType = 'info';
        }
      } catch (error) {
        console.error('Error fetching saved stories:', error);
        this.statusMessage = error.response?.data?.detail || 'Failed to load saved stories';
        this.statusType = 'error';
      } finally {
        this.loading = false;
      }
    },

    async refreshList() {
      await this.fetchSavedStories()
    },

    async loadStory(filename) {
      this.loadingStory = filename
      try {
        const story = await storyService.loadSavedStory(filename)
        this.$store.commit('SET_CURRENT_STORY', story)
        this.$store.commit('ADD_STORY', story)
        this.$router.push({ name: 'ViewStory', params: { id: story.id } })
      } catch (error) {
        console.error('Error loading story:', error)
        this.showStatus('Failed to load story', 'error')
      } finally {
        this.loadingStory = null
      }
    },

    async downloadStory(filename) {
      try {
        await storyService.downloadStory(filename)
        this.showStatus('Story downloaded successfully', 'success')
      } catch (error) {
        console.error('Error downloading story:', error)
        this.showStatus('Failed to download story', 'error')
      }
    },

    async deleteStory(filename) {
      if (!confirm('Are you sure you want to delete this story?')) {
        return;
      }

      try {
        console.log(`Deleting story: ${filename}`);
        await storyService.deleteSavedStory(filename);
        this.showStatus('Story deleted successfully', 'success');

        // Refresh the list
        await this.fetchSavedStories();
      } catch (error) {
        console.error('Error deleting story:', error);
        this.showStatus(error.response?.data?.detail || 'Failed to delete story', 'error');
      }
    },

    async handleFileUpload(event) {
      const file = event.target.files[0]
      if (!file) return

      this.uploading = true
      try {
        const response = await storyService.uploadStory(file)
        this.$store.commit('SET_CURRENT_STORY', response.story)
        this.$store.commit('ADD_STORY', response.story)
        this.showStatus('Story uploaded successfully', 'success')

        // Navigate to view the story
        setTimeout(() => {
          this.$router.push({ name: 'ViewStory', params: { id: response.story.id } })
        }, 1000)
      } catch (error) {
        console.error('Error uploading story:', error)
        this.showStatus('Failed to upload story', 'error')
      } finally {
        this.uploading = false
        // Reset file input
        this.$refs.fileInput.value = ''
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'Unknown date'
      const date = new Date(dateString)
      return date.toLocaleDateString()
    },

    showStatus(message, type) {
      this.statusMessage = message
      this.statusType = type
      setTimeout(() => {
        this.statusMessage = ''
        this.statusType = ''
      }, 5000)
    }
  }
}
</script>