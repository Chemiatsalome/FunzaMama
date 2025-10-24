# AI Service Setup Guide

## 🚀 Multiple AI Provider Support

The chatbot now supports multiple AI providers with automatic fallback. This helps avoid rate limits and provides better reliability.

## 📋 Supported Providers

### 1. OpenAI (Recommended)
- **Most reliable and consistent**
- **Cost**: ~$0.002 per 1K tokens
- **Setup**: Get API key from https://platform.openai.com/api-keys

```bash
# Add to your .env file
OPENAI_API_KEY=sk-your-openai-key-here
```

### 2. Anthropic Claude
- **High quality responses**
- **Cost**: ~$0.003 per 1K tokens
- **Setup**: Get API key from https://console.anthropic.com/

```bash
# Add to your .env file
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

### 3. Google Gemini
- **Free tier available**
- **Cost**: Free up to 15 requests/minute
- **Setup**: Get API key from https://makersuite.google.com/app/apikey

```bash
# Add to your .env file
GOOGLE_API_KEY=your-google-api-key-here
```

### 4. Together AI (Current)
- **Your current provider**
- **Cost**: Varies by model
- **Setup**: Already configured

```bash
# Add to your .env file
TOGETHER_API_KEY=your-together-key-here
```

## 🔧 Installation

Install the required packages:

```bash
# For OpenAI
pip install openai

# For Anthropic
pip install anthropic

# For Google Gemini
pip install google-generativeai

# For Together AI (already installed)
pip install together
```

## 🎯 How It Works

1. **Priority Order**: The system tries providers in order of preference
2. **Automatic Fallback**: If one provider fails, it tries the next
3. **Rate Limit Handling**: Automatically switches providers when rate limits are hit
4. **Offline Mode**: Falls back to keyword-based responses if all providers fail

## 📊 Provider Comparison

| Provider | Reliability | Speed | Cost | Quality |
|----------|-------------|-------|------|---------|
| OpenAI | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Anthropic | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Google | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Together | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🚀 Quick Start

1. **Choose your preferred provider** (OpenAI recommended)
2. **Get an API key** from the provider's website
3. **Add it to your .env file**
4. **Restart your Flask app**

The system will automatically detect and use your configured providers!

## 💡 Tips

- **Start with OpenAI** for the best experience
- **Add Google Gemini** as a free backup
- **Keep Together AI** as a fallback
- **Monitor usage** to avoid unexpected costs
