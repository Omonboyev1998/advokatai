"""
ADVOKAT AI — Modelni o'qitish (Fine-Tuning) skripti.
Ushbu skript exports/advokat_ai_sft_chatml.jsonl dataseti asosida
Qwen 2.5 (yoki LLaMA 3.1) modelini Unsloth yordamida o'qitadi va GGUF formatiga o'tkazadi.
"""

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATASET_FILE = HERE / "exports" / "advokat_ai_sft_chatml.jsonl"


def train():
    print("=" * 60)
    print("⚖️  ADVOKAT AI — FINE-TUNING BOSHLANMOQDA")
    print("=" * 60)

    if not DATASET_FILE.exists():
        print(f"❌ Xatolik: Dataset fayli topilmadi: {DATASET_FILE}")
        sys.exit(1)

    print(f"📂 Dataset: {DATASET_FILE}")

    try:
        from unsloth import FastLanguageModel
        import torch
        from datasets import load_dataset
        from trl import SFTTrainer
        from transformers import TrainingArguments
    except ImportError:
        print("\n⚠️  O'qitish kutubxonalari o'rnatilmagan.")
        print("Google Colab yoki GPU serverda quyidagilarni o'rnating:")
        print("  pip install \"unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git\"")
        print("  pip install --no-deps trl peft accelerate bitsandbytes datasets")
        return

    # 1. Asosiy modelni yuklash
    print("\n1. Asosiy model (Qwen 2.5-3B-Instruct) yuklanmoqda...")
    max_seq_length = 2048
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="Qwen/Qwen2.5-3B-Instruct",
        max_seq_length=max_seq_length,
        load_in_4bit=True,
    )

    # 2. LoRA adapterlarini ulash
    print("\n2. LoRA adapterlari sozlanmoqda...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
    )

    # 3. Datasetni yuklash
    print("\n3. Yuridik dataset yuklanmoqda...")
    dataset = load_dataset("json", data_files=str(DATASET_FILE), split="train")
    print(f"Jami namunalar soni: {len(dataset)}")

    # 4. O'qitish jarayoni
    print("\n4. Modelni o'qitish boshlanmoqda...")
    output_dir = str(HERE / "advokat_ai_weights")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="messages",
        max_seq_length=max_seq_length,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=10,
            max_steps=300,
            learning_rate=2e-4,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=10,
            output_dir=output_dir,
        ),
    )
    trainer.train()

    # 5. GGUF formatiga eksport qilish (Mark 57 / Ollama / LM Studio uchun)
    print("\n5. Model GGUF (q4_k_m) formatiga o'tkazilmoqda...")
    gguf_dir = str(HERE / "advokat_qwen2.5_gguf")
    model.save_pretrained_gguf(gguf_dir, tokenizer, quantization_method="q4_k_m")
    print(f"\n✅ Tayyor! O'qitilgan model saqlandi: {gguf_dir}")


if __name__ == "__main__":
    train()
