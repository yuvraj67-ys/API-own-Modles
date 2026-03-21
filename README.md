cat > README.md << 'EOF'
# 🎨 My AI Hub API

Personal AI API for Image & Song Generation using Hugging Face (Free Tier)

## 🚀 Deploy on Render

1. Fork this repo
2. Go to https://render.com → New Web Service
3. Connect your repo
4. Add Environment Variables (see below)
5. Deploy!

## 🔑 Required Environment Variables

| Key | Value |
|-----|-------|
| `HF_API_TOKEN` | Your Hugging Face token |
| `API_SECRET_KEY` | Random secret string |
| `ADMIN_KEYS` | Comma-separated admin keys |

## 📡 API Endpoints

- `GET /` - Status
- `GET /docs` - Interactive docs
- `POST /api/v1/imagegen` - Generate image
- `POST /api/v1/songgen` - Generate song
- `GET /api/v1/songgen/presets` - Get music presets

## 🧪 Test

```bash
curl https://your-api.onrender.com/ping
```

## 📄 License

MIT - Use freely!
EOF
