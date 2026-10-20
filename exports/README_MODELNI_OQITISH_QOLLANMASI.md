# ADVOKAT AI — UNIVERSAL MODEL O'QITISH (FINE-TUNING) MA'LUMOTLAR TO'PLAMI

Ushbu to'plam O'zbekiston Respublikasi amaliyotchi advokatlari taktikasi, 11 ta huquqiy soha,
64 ta nizo arxetipi, 6 000+ ta qonun moddalari hamda 4 900+ ta fuqarolar savol-javoblarini o'z ichiga oladi.

## 📁 FAYLLAR TARKIBI VA VAZIFALARI

1. **`advokat_ai_sft_chatml.jsonl`** (8,186 ta to'liq dialog):
   - **Formati:** `messages: [system, user, assistant]`
   - **Mos keladigan vositalar:**
     - Unsloth (Eng tezkor LoRA/QLoRA o'qitish)
     - Hugging Face `SFTTrainer` (TRL)
     - LLaMA-Factory
     - OpenAI Fine-Tuning API (GPT-4o-mini / GPT-3.5)
     - Axolotl, vLLM

2. **`advokat_ai_alpaca_instructions.json`** (8,186 ta instruksiya):
   - **Formati:** `[ {"instruction": "...", "input": "...", "output": "..."} ]`
   - **Mos keladigan vositalar:** Stanford Alpaca, FastChat, Qwen-Instruct tuning, Torchtune.

3. **`advokat_ai_raw_corpus.txt`**:
   - **Formati:** Yaxlit uzluksiz toza yuridik matn korpusi.
   - **Vazifasi:** Continued Pre-Training (CPT), Domain Adaptation, yoki RAG (FAISS/Chroma) embeddinglari yaratish.

---

## 🚀 MODELLARNI O'QITISH (QO'LLANMA)

### 1. Qaysi asosiy modellarni o'qitish tavsiya etiladi?
- **Qwen 2.5 (1.5B, 3B, 7B yoki 14B)**: O'zbek va ko'p tilli korpusda eng yuqori natija beradi.
- **LLaMA 3.1 (8B)**: Kuchli mantiqiy xulosalar va dalillarni tahlil qilish uchun.
- **Gemma 2 (2B, 9B)**: Google arxitekturasi asosida.

### 2. Google Colab (Bepul T4 GPU) orqali Unsloth bilan o'qitish:
```python
from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# 1. Modelni yuklash
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "Qwen/Qwen2.5-3B-Instruct",
    max_seq_length = 2048,
    load_in_4bit = True,
)

# 2. LoRA adapterlarini ulash
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
)

# 3. Bizning advokat_ai_sft_chatml.jsonl datasetimizni yuklash
dataset = load_dataset("json", data_files="advokat_ai_sft_chatml.jsonl", split="train")

# 4. O'qitish (SFTTrainer)
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "messages",
    max_seq_length = 2048,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 10,
        max_steps = 250,
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 10,
        output_dir = "advokat_ai_weights",
    ),
)
trainer.train()

# 5. GGUF formatiga eksport qilish (Oflayn foydalanish uchun)
model.save_pretrained_gguf("advokat_qwen2.5_trained", tokenizer, quantization_method = "q4_k_m")
```

### 3. OpenAI orqali Fine-Tuning qilish:
1. OpenAI platformasiga kiring (`platform.openai.com`).
2. **Fine-tuning** bo'limiga o'ting.
3. `advokat_ai_sft_chatml.jsonl` faylini yuklang.
4. Base model sifatida `gpt-4o-mini` ni tanlang va 'Create' tugmasini bosing.
