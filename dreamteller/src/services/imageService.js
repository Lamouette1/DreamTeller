import axios from 'axios'

const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api'

export default {
  async generateImage(imagePrompt) {
    try {
      const response = await axios.post(`${API_URL}/images/generate`, { prompt: imagePrompt })
      return response.data.imageUrl
    } catch (error) {
      console.error('Error generating image:', error)
      throw error
    }
  }
}