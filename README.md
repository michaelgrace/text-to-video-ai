# Text-To-Video AI 🎬

Generate engaging videos from text using AI. This project combines OpenAI's GPT for script generation, Pexels for video content, and advanced text-to-speech for narration.

## Features

- 🤖 AI-powered script generation
- 🎥 Automatic video content selection and assembly
- 🔊 High-quality text-to-speech narration
- 📝 Automatic caption generation and synchronization
- 🖥️ GPU-accelerated video processing (where available)
- 🎨 Theme-based content selection
- 💾 Smart content caching

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/YourUsername/Text-To-Video-AI.git
cd Text-To-Video-AI
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY
# - PEXELS_API_KEY
```

3. Run with Docker Compose:
```bash
docker-compose up --build
```

4. Access the web interface:
```
http://localhost:7701
```

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py "Your topic here"
```

## Project Structure

```
Text-To-Video-AI/
├── app/                    # Core application code
│   ├── core/              # Core functionality
│   └── utils/             # Utility functions
├── config/                # Configuration files
├── web/                   # Web interface
├── exports/              # Generated content
└── temp/                 # Temporary files
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `PEXELS_API_KEY`: Your Pexels API key
- `VOICE_PROVIDER`: Voice service provider (default: "kokoro")
- `DEBUG_MODE`: Enable debug logging (default: false)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments

- OpenAI GPT for script generation
- Pexels for video content
- MoviePy for video processing
- Streamlit for the web interface
