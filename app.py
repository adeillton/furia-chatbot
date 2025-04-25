import os
import warnings
from flask import Flask, request, jsonify, render_template
from transformers import pipeline
import torch

# Configuração para Mac com M1/M2
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
warnings.filterwarnings("ignore")

# Dados da FURIA (julho/2024)
DADOS_FURIA = {
    "cs2": {
        "elenco": ["FalleN (IGL)", "KSCERATO", "yuurih", "chelo", "arT"],
        "prox_jogo": "IEM Dallas 2024 - 05/08 vs Vitality",
        "titulos": ["IEM Dallas 2022", "ESL Pro League S15"],
        "stream": "twitch.tv/furiagg"
    },
    "valorant": {
        "elenco": ["dgzin", "qck", "Mazino", "frz", "Khalil"],
        "prox_jogo": "VCT Americas - 12/08 vs LOUD",
        "stream": "twitch.tv/furiagg"
    }
}

app = Flask(__name__)

# Carrega o modelo
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
        print(f"❌ Erro ao carregar modelo: {str(e)}")
        return None

chatbot = load_model()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "").lower().strip()
        if not user_message:
            return jsonify({"reply": "🧠 Pergunta algo sobre a FURIA! Pode ser sobre elenco, jogos ou curiosidades."})

        # Respostas diretas (sem IA)
        if "elenco" in user_message:
            if "cs2" in user_message:
                return jsonify({"reply": f"👥 Elenco CS2: {', '.join(DADOS_FURIA['cs2']['elenco'])}"})
            elif "valorant" in user_message:
                return jsonify({"reply": f"💥 Elenco Valorant: {', '.join(DADOS_FURIA['valorant']['elenco'])}"})
            return jsonify({"reply": "📌 Especifique o jogo: 'elenco cs2' ou 'elenco valorant'."})

        elif "próximo jogo" in user_message or "proximo jogo" in user_message:
            if "cs2" in user_message:
                return jsonify({"reply": f"📅 {DADOS_FURIA['cs2']['prox_jogo']}\n🎥 {DADOS_FURIA['cs2']['stream']}"})
            elif "valorant" in user_message:
                return jsonify({"reply": f"📅 {DADOS_FURIA['valorant']['prox_jogo']}\n🎥 {DADOS_FURIA['valorant']['stream']}"})
            return jsonify({"reply": "📌 Especifique: 'próximo jogo cs2' ou 'próximo jogo valorant'."})

        # Resposta via IA com vibe fan-clube
        if chatbot:
            prompt = f"""
Você é o FURIA Bot, o assistente oficial da torcida da FURIA Esports. Sua missão é responder com empolgação, criatividade e paixão pelo time. Seja curto, direto e com muito entusiasmo!

Usuário: {user_message}
FURIA Bot:"""

            resposta = chatbot(
                prompt,
                max_new_tokens=100,
                temperature=0.9,
                do_sample=True,
                top_p=0.95,
                num_return_sequences=1
            )[0]["generated_text"]

            # Extrair a parte gerada após "FURIA Bot:"
            if "FURIA Bot:" in resposta:
                resposta_limpa = resposta.split("FURIA Bot:")[-1].strip().split("\n")[0]
            else:
                resposta_limpa = resposta.strip()

            if resposta_limpa:
                return jsonify({"reply": resposta_limpa})
            else:
                return jsonify({"reply": "🔥 Bora torcer pela FURIA! Pergunta algo mais pra mim."})

        return jsonify({"reply": "⚠️ Estou sem acesso à IA agora. Tente algo sobre elenco ou próximos jogos!"})

    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"reply": "🚨 Deu ruim no servidor! Tenta de novo, guerreiro!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
