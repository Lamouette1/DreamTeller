import axios from 'axios'

const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000'

export default {
  async generateImage(imagePrompt) {
    try {
      const response = await axios.post(`${API_URL}/api/images/generate`, { prompt: imagePrompt })
      console.log("Sending story prompt to server:", JSON.stringify(imagePrompt))
      console.log("Received response from server:", response.data)
      return response.data.imageUrl
    } catch (error) {
      console.error('Error generating image:', error)
      throw error
    }
  }
}