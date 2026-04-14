from __future__ import annotations

import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer


MODEL_ID = "google/gemma-4-E2B-it"
DEFAULT_HUB_MODEL_ID = "YOUR_HF_USERNAME/ayda-gemma4-e2b-tr-seed-lora-v1"
DATA_PATH = Path(__file__).with_name("ayda_seed_sft.jsonl")


def load_seed_rows() -> list[dict]:
    rows: list[dict] = []
    with DATA_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            messages = item["messages"]
            rows.append(
                {
                    "prompt": messages[:-1],
                    "completion": [messages[-1]],
                    "tag": item.get("tag", "general"),
                }
            )
    return rows


def main() -> None:
    rows = load_seed_rows()
    dataset = Dataset.from_list(rows)
    split = dataset.train_test_split(test_size=0.125, seed=42)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token or tokenizer.bos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        attn_implementation="sdpa",
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model)

    peft_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "v_proj"],
    )

    args = SFTConfig(
        output_dir="ayda-gemma4-e2b-tr-seed-lora-v1",
        hub_model_id=DEFAULT_HUB_MODEL_ID,
        push_to_hub=False,
        learning_rate=1e-4,
        num_train_epochs=4,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=16,
        warmup_ratio=0.1,
        lr_scheduler_type="cosine",
        logging_steps=1,
        save_strategy="epoch",
        eval_strategy="epoch",
        save_total_limit=2,
        max_length=512,
        report_to=["trackio"],
        project="ayda-persona",
        run_name="gemma4-e2b-tr-seed-sft-v1",
    )

    trainer = SFTTrainer(
        model=model,
        args=args,
        train_dataset=split["train"],
        eval_dataset=split["test"],
        processing_class=tokenizer,
        peft_config=peft_config,
    )

    trainer.train()
    trainer.save_model(args.output_dir)
    print(
        {
            "output_dir": args.output_dir,
            "train_size": len(split["train"]),
            "eval_size": len(split["test"]),
        }
    )


if __name__ == "__main__":
    main()
