from fastapi import FastAPI, Query
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = FastAPI()

# Função para extrair o ID do vídeo do YouTube
def extrair_video_id(url: str):
    """
    Extrai o ID do vídeo a partir da URL do YouTube.
    """
    padrao = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(padrao, url)
    return match.group(1) if match else None

# Criar um endpoint para transcrição
@app.get("/transcrever")
def transcrever_video(youtube_url: str = Query(..., title="Seu link do YouTube")):
    """
    Endpoint que recebe a URL de um vídeo do YouTube e retorna sua transcrição.
    Ele tenta buscar a transcrição nos idiomas: Espanhol, Português do Brasil, Português e Inglês.
    """
    video_id = extrair_video_id(youtube_url)

    if not video_id:
        return {"error": "URL inválida. Verifique se o link está correto."}

    try:
        # Lista de idiomas suportados
        idiomas = ["pt-BR", "pt", "es", "en"]  # Português Brasil, Português, Espanhol, Inglês
        transcricao = None
        idioma_detectado = None

        for idioma in idiomas:
            try:
                transcricao = YouTubeTranscriptApi.get_transcript(video_id, languages=[idioma])
                idioma_detectado = idioma
                break  # Sai do loop se conseguir a transcrição
            except Exception:
                continue  # Tenta o próximo idioma

        if not transcricao:
            return {"error": "Nenhuma transcrição disponível para este vídeo nos idiomas suportados."}

        # Converter a transcrição para texto simples
        texto_transcrito = " ".join([item["text"] for item in transcricao])

        return {"transcricao": texto_transcrito, "idioma_detectado": idioma_detectado}

    except Exception as e:
        return {"error": f"Erro ao processar a transcrição: {str(e)}"}

# Rota de teste para verificar se a API está rodando
@app.get("/")
def home():
    return {"mensagem": "API de Transcrição rodando no Render!"}

# Executar a API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
