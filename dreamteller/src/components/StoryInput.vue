<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Create Your Dream Story</h2>
    
    <form @submit.prevent="submitStoryPrompt">
      <!-- Story Idea Input -->
      <div class="mb-6">
        <label for="storyIdea" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Describe Your Story Idea
        </label>
        <textarea
          id="storyIdea"
          v-model="storyPrompt.idea"
          rows="4"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          placeholder="e.g., A young wizard discovers a hidden door in the forest that leads to a parallel universe..."
          required
        ></textarea>
      </div>

      <!-- Genre Selection -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Select Genre
        </label>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
          <label v-for="genre in genres" :key="genre" class="flex items-center p-3 border rounded-md cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700" :class="{ 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30': storyPrompt.genre === genre, 'border-gray-300 dark:border-gray-600': storyPrompt.genre !== genre }">
            <input type="radio" :value="genre" v-model="storyPrompt.genre" class="sr-only" />
            <span class="ml-2 text-gray-700 dark:text-gray-300">{{ genre }}</span>
          </label>
        </div>
      </div>

      <!-- Tone Selection -->
      <div class="mb-6">
        <label for="tone" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Story Tone
        </label>
        <select
          id="tone"
          v-model="storyPrompt.tone"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        >
          <option v-for="tone in tones" :key="tone" :value="tone">{{ tone }}</option>
        </select>
      </div>

      <!-- Scene Count Selector -->
      <div class="mb-6">
        <label for="sceneCount" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Number of Scenes (3-10)
        </label>
        <div class="flex items-center">
          <input 
            type="range" 
            id="sceneCount" 
            v-model.number="storyPrompt.numScenes" 
            min="3" 
            max="10" 
            step="1" 
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          />
          <span class="ml-3 w-10 text-center text-gray-700 dark:text-gray-300 font-medium">
            {{ storyPrompt.numScenes }}
          </span>
        </div>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          More scenes create a longer, more detailed story
        </p>
      </div>

      <!-- Main Character Input -->
      <div class="mb-6">
        <label for="mainCharacter" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Main Character Description (Optional)
        </label>
        <input
          id="mainCharacter"
          v-model="storyPrompt.mainCharacter"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          placeholder="e.g., A brave young girl with freckles and a curious mind"
        />
      </div>

      <!-- Setting Input -->
      <div class="mb-6">
        <label for="setting" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Story Setting (Optional)
        </label>
        <input
          id="setting"
          v-model="storyPrompt.setting"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          placeholder="e.g., A medieval village surrounded by enchanted woods"
        />
      </div>

      <!-- Art Style Input -->
      <div class="mb-6">
        <label for="artStyle" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Art Style for Illustrations
        </label>
        <select
          id="artStyle"
          v-model="storyPrompt.artStyle"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        >
          <option v-for="style in artStyles" :key="style" :value="style">{{ style }}</option>
        </select>
      </div>
      
      <!-- Submit Button -->
      <div class="flex justify-end">
        <button
          type="submit"
          class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          :disabled="loading"
        >
          <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ loading ? 'Generating Story...' : 'Generate Story' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  name: 'StoryInput',
  data() {
    return {
      storyPrompt: {
        idea: '',
        genre: 'Fantasy',
        tone: 'Lighthearted',
        mainCharacter: '',
        setting: '',
        artStyle: 'Digital Painting',
        numScenes: 5
      },
      genres: [
        'Fantasy', 
        'Science Fiction', 
        'Mystery', 
        'Adventure', 
        'Romance', 
        'Horror'
      ],
      tones: [
        'Lighthearted',
        'Serious',
        'Funny',
        'Dramatic',
        'Mysterious',
        'Educational',
        'Inspirational'
      ],
      artStyles: [
        'Digital Painting',
        'Watercolor',
        'Pixel Art',
        'Comic Book',
        '3D Rendered',
        'Children\'s Book Illustration',
        'Concept Art'
      ],
      loading: false
    }
  },
  methods: {
    async submitStoryPrompt() {
      this.loading = true
      try {
        await this.$store.dispatch('generateStory', this.storyPrompt)
        this.$router.push({ name: 'ViewStory', params: { id: this.$store.state.currentStory.id } })
      } catch (error) {
        console.error('Error generating story:', error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>