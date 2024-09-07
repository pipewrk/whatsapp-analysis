# Define token values and pricing for each model
input_tokens = 4_000_000  # 4M input tokens (due to 4 steps)
output_tokens = 500_000    # 500k output tokens (same as before)

pricing_table = {
    "gpt-4o": {
        "input_token_price": 5.00,
        "output_token_price": 15.00,
        "input_token_price_batch": 2.50,
        "output_token_price_batch": 7.50
    },
    "gpt-4o-2024-08-06": {
        "input_token_price": 2.50,
        "output_token_price": 10.00,
        "input_token_price_batch": 1.25,
        "output_token_price_batch": 5.00
    },
    "gpt-4o-2024-05-13": {
        "input_token_price": 5.00,
        "output_token_price": 15.00,
        "input_token_price_batch": 2.50,
        "output_token_price_batch": 7.50
    },
    "gpt-4o-mini": {
        "input_token_price": 0.150,
        "output_token_price": 0.600,
        "input_token_price_batch": 0.075,
        "output_token_price_batch": 0.300
    }
}

# Calculate cost for each model
costs = {}
for model, pricing in pricing_table.items():
    # Normal cost
    input_cost_normal = (input_tokens / 1_000_000 * pricing["input_token_price"])
    output_cost_normal = (output_tokens / 1_000_000 * pricing["output_token_price"])
    total_cost_normal = input_cost_normal + output_cost_normal
    
    # Batch cost
    input_cost_batch = (input_tokens / 1_000_000 * pricing["input_token_price_batch"])
    output_cost_batch = (output_tokens / 1_000_000 * pricing["output_token_price_batch"])
    total_cost_batch = input_cost_batch + output_cost_batch
    
    costs[model] = {
        "input_cost_normal": round(input_cost_normal, 2),
        "output_cost_normal": round(output_cost_normal, 2),
        "total_cost_normal": round(total_cost_normal, 2),
        "input_cost_batch": round(input_cost_batch, 2),
        "output_cost_batch": round(output_cost_batch, 2),
        "total_cost_batch": round(total_cost_batch, 2)
    }

# Print out the results
print(f"{'Model':<20} {'Input Cost':<15} {'Output Cost':<15} {'Total Cost':<15}")
print("-" * 65)
for model, pricing in costs.items():
    print(f"{model:<20} ${pricing['input_cost_normal']:<14} ${pricing['output_cost_normal']:<14} ${pricing['total_cost_normal']:<14}")
print("\n")
print(f"{'Model':<20} {'Input Cost (Batch)':<18} {'Output Cost (Batch)':<18} {'Total Cost (Batch)':<18}")
print("-" * 75)
for model, pricing in costs.items():
    print(f"{model:<20} ${pricing['input_cost_batch']:<17} ${pricing['output_cost_batch']:<17} ${pricing['total_cost_batch']:<17}")
