import os
import warnings
from flask import Flask, request, jsonify, render_template
from transformers import pipeline
import torch
import random
import datetime

# Configuração para Mac com M1/M2
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
warnings.filterwarnings("ignore")

# Dados atualizados da FURIA CS2
DADOS_CS2 = {
    "elenco": ["FalleN (IGL)", "KSCERATO", "yuurih", "molodoy", "YEKINDAR"],  # Atualize com jogadores atuais
    "prox_jogo": "PGL Astana 2025 – data a confirmar",  # Atualizar com a data real quando disponível
    "titulos": [
        "IEM Dallas 2022",
        "ESL Pro League S15",
        "PGL Major Copenhagen 2024"  # Atualizar com mais títulos se houver
    ],
    "stream": "https://twitch.tv/furiagg",  # Link para a transmissão da FURIA
    "contato": "https://wa.me/5511993404466"  # Link para contato pelo WhatsApp
}


app = Flask(__name__)

# Carrega o modelo TinyLlama

def load_model():
    try:
        print("⏳ Carregando modelo IA...")
        model = pipeline(
            "text-generation",
            model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            device="mps" if torch.backends.mps.is_available() else "cpu",
            torch_dtype=torch.float16
        )
        print("✅ IA carregada com sucesso!")
        return model
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return None

chatbot = load_model()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip().lower()
    if not user_message:
        return jsonify({"reply": "🧠 Manda uma pergunta sobre CS2, torcedor!"})

    # Boas-vindas
    if user_message in ["oi", "olá", "e aí", "fala aí", "bom dia", "boa tarde"]:
        return jsonify({"reply": "🎧 E aí, fã de CS2! Pergunte sobre elenco, próximos jogos ou títulos da FURIA."})

    # Respostas fixas CS2
    if "elenco" in user_message:
        return jsonify({"reply": f"👥 Nosso lineup de CS2: {', '.join(DADOS_CS2['elenco'])}"})

    if "próximo jogo" in user_message or "proximo jogo" in user_message:
        return jsonify({"reply": f"📅 Próximo CS2: {DADOS_CS2['prox_jogo']} 🎥 {DADOS_CS2['stream']}"})

    if "título" in user_message or "titulos" in user_message:
        return jsonify({"reply": f"🏆 Títulos CS2: {', '.join(DADOS_CS2['titulos'])}"})

    # Comandos extras
    if "stream" in user_message or "ao vivo" in user_message:
        return jsonify({"reply": f"📺 Assista ao vivo: {DADOS_CS2['stream']}"})

    if "contato" in user_message or "whatsapp" in user_message:
        return jsonify({"reply": f"🤖 Fale com a FURIA: {DADOS_CS2['contato']}"})

    if "cheer" in user_message or "comemorar" in user_message:
        cheers = [
            "🔥 Vai FURIA, mostra o que é raça! 🔥",
            "🐆 Ruge, torcedor, a FURIA é nossa paixão! 🐆",
            "🎮 CS2 só com a FURIA — vamo que vamo! 🎮"
        ]
        return jsonify({"reply": random.choice(cheers)})

    if "countdown" in user_message or "contagem" in user_message:
        # Calcula dias para o próximo jogo
        data_str = DADOS_CS2['prox_jogo'].split(" - ")[1].split(" vs")[0]  # ex: "05/08"
        day, month = map(int, data_str.split("/"))
        hoje = datetime.date.today()
        ano = hoje.year
        jogo = datetime.date(ano, month, day)
        delta = (jogo - hoje).days
        return jsonify({"reply": f"⏳ Faltam {delta} dias para o próximo CS2!"})

    # IA para demais perguntas
    if chatbot:
        prompt = f"""
Você é o FURIA Bot, assistente oficial e torcedor fanático de CS2 da FURIA Esports.
Responda empolgado, com emojis e bordões, mas seja claro e sucinto.

Usuário: {user_message}
FURIA Bot:"""
        gerado = chatbot(
            prompt,
            max_new_tokens=100,
            temperature=0.8,
            top_p=0.9,
            do_sample=True,
            num_return_sequences=1
        )[0]["generated_text"]
        if "FURIA Bot:" in gerado:
            resposta = gerado.split("FURIA Bot:")[-1].strip().split("\n")[0]
        else:
            resposta = gerado.strip().split("\n")[0]
        return jsonify({"reply": resposta or "🔥 Vamos com tudo, FURIA CS2!"})

    return jsonify({"reply": "⚠️ Estou sem IA agora. Pergunte sobre CS2!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)