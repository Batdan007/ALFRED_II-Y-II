# 3. Local LLM + GPT‑4 Refinement


import os
import json
import openai
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# --------------------
# 1. Set up local LLM
# --------------------
local_model_name = "meta-llama/Meta-Llama-3-8B"
tokenizer = AutoTokenizer.from_pretrained(local_model_name)
model = AutoModelForCausalLM.from_pretrained(local_model_name, device_map="auto", torch_dtype=torch.float16)

def local_inference(prompt, max_length=150):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=max_length)
    return tokenizer.decode(output[0], skip_special_tokens=True)

# -------------------------
# 2. Set up OpenAI GPT‑4
# -------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_openai(prompt, tool_response=None):
    # Build the message list. If we're already inside a tool call, pass that.
    messages = []
    if tool_response:
        messages.append({"role": "tool", "content": tool_response})
    messages.append({"role": "assistant", "content": prompt})

    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return resp.choices[0].message.content

# -------------------------
# 3. The cooperative loop
# -------------------------
if __name__ == "__main__":
    # 1️⃣ Ask local model for a question or idea
    local_prompt = "Draft a brief explanation of how a convolutional neural network works."
    local_output = local_inference(local_prompt)
    print("Local LLM:", local_output)

    # 2️⃣ Pass that output to GPT‑4 for refinement
    refine_prompt = f"Refine and expand the following explanation:\n\n{local_output}"
    gpt_response = call_openai(refine_prompt)
    print("\nGPT‑4 refined:", gpt_response)
