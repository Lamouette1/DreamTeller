import { createStore } from 'vuex'
import storyService from '../services/storyService'
import imageService from '../services/imageService'

export default createStore({
  state: {
    currentStory: null,
    stories: [],
    loading: false,
    error: null
  },
  getters: {
    getStoryById: (state) => (id) => {
      return state.stories.find(story => story.id === id) || null
    }
  },
  mutations: {
    SET_CURRENT_STORY(state, story) {
      state.currentStory = story
    },
    ADD_STORY(state, story) {
      state.stories.push(story)
    },
    SET_LOADING(state, isLoading) {
      state.loading = isLoading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    UPDATE_SCENE_TEXT(state, { sceneIndex, newText }) {
      if (state.currentStory && state.currentStory.scenes) {
        state.currentStory.scenes[sceneIndex].text = newText
      }
    },
    UPDATE_SCENE_IMAGE(state, { sceneIndex, newImageUrl }) {
      if (state.currentStory && state.currentStory.scenes) {
        state.currentStory.scenes[sceneIndex].imageUrl = newImageUrl
      }
    }
  },
  actions: {
    async generateStory({ commit }, storyPrompt) {
			try {
				commit('SET_LOADING', true)
				commit('SET_ERROR', null)
				
				// Call the API to generate a story
				const story = await storyService.generateStory(storyPrompt)
				
				// Process each scene to generate images
				for (let i = 0; i < story.scenes.length; i++) {
					const scene = story.scenes[i]
					if (!scene.imageUrl && scene.imagePrompt) {
						try {
							scene.imageUrl = await imageService.generateImage(scene.imagePrompt)
						} catch (error) {
							console.error(`Failed to generate image for scene ${i}:`, error)
						}
					}
				}
				
				commit('SET_CURRENT_STORY', story)
				commit('ADD_STORY', story)
				return story
			} catch (error) {
				commit('SET_ERROR', error.message || 'Failed to generate story')
				throw error
			} finally {
				commit('SET_LOADING', false)
			}
		},

    async regenerateSceneText({ commit, state }, sceneIndex) {
      try {
        commit('SET_LOADING', true)

        const scene = state.currentStory.scenes[sceneIndex]
        const newText = await storyService.regenerateSceneText(
          state.currentStory.prompt, 
          scene.text,
          sceneIndex
        )
        
        commit('UPDATE_SCENE_TEXT', { sceneIndex, newText })
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to regenerate scene text')
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async regenerateSceneImage({ commit, state }, sceneIndex) {
			try {
					commit('SET_LOADING', true)
					
					const scene = state.currentStory.scenes[sceneIndex]
					// Use imagePrompt if available, otherwise generate one
					const prompt = scene.imagePrompt || 
					`${state.currentStory.prompt.setting || ''}, ${scene.text}, ${state.currentStory.prompt.artStyle}`
					
					const newImageUrl = await imageService.generateImage(prompt)
					
					commit('UPDATE_SCENE_IMAGE', { sceneIndex, newImageUrl })
			} catch (error) {
					commit('SET_ERROR', error.message || 'Failed to regenerate scene image')
			} finally {
					commit('SET_LOADING', false)
			}
    }
  }
})
