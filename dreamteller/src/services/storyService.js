import axios from 'axios'

const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api'

export default {
  async generateStory(storyPrompt) {
    try {
      const response = await axios.post(`${API_URL}/stories/generate`, storyPrompt)
      return response.data
    } catch (error) {
      console.error('Error generating story:', error)
      throw error
    }
  },
  
  async regenerateSceneText(prompt, currentText, sceneIndex) {
    try {
      const response = await axios.post(`${API_URL}/stories/regenerate-text`, {
        prompt,
        currentText,
        sceneIndex
      })
      return response.data.text
    } catch (error) {
      console.error('Error regenerating scene text:', error)
      throw error
    }
  },
  
  async getStories() {
    try {
      const response = await axios.get(`${API_URL}/stories`)
      return response.data
    } catch (error) {
      console.error('Error fetching stories:', error)
      throw error
    }
  }
}
