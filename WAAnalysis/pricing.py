import logging
from WAAnalysis.config import ERROR_LOGS_DIRECTORY
from WAAnalysis.utils import ensure_directories_exist

# -------------------------------
# Setup Logging
# -------------------------------
log_file = ERROR_LOGS_DIRECTORY / "pricing_analysis.log"
ensure_directories_exist([ERROR_LOGS_DIRECTORY])

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

logging.getLogger().addHandler(console_handler)

# -------------------------------
# Pricing Configuration
# -------------------------------

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

# -------------------------------
# Cost Calculation Function
# -------------------------------

def calculate_costs():
    """Calculates and logs cost analysis for each model."""
    costs = {}
    
    # Calculate cost for each model
    for model, pricing in pricing_table.items():
        # Normal cost
        input_cost_normal = (input_tokens / 1_000_000 * pricing["input_token_price"])
        output_cost_normal = (output_tokens / 1_000_000 * pricing["output_token_price"])
        total_cost_normal = input_cost_normal + output_cost_normal
        
        # Batch cost
        input_cost_batch = (input_tokens / 1_000_000 * pricing["input_token_price_batch"])
        output_cost_batch = (output_tokens / 1_000_000 * pricing["output_token_price_batch"])
        total_cost_batch = input_cost_batch + output_cost_batch
        
        # Store costs in dictionary
        costs[model] = {
            "input_cost_normal": round(input_cost_normal, 2),
            "output_cost_normal": round(output_cost_normal, 2),
            "total_cost_normal": round(total_cost_normal, 2),
            "input_cost_batch": round(input_cost_batch, 2),
            "output_cost_batch": round(output_cost_batch, 2),
            "total_cost_batch": round(total_cost_batch, 2)
        }

    # Log the analysis results
    log_cost_analysis(costs)
    return costs

# -------------------------------
# Logging Cost Analysis
# -------------------------------

def log_cost_analysis(costs):
    """Logs cost analysis results."""
    logging.info(f"{'Model':<20} {'Input Cost':<15} {'Output Cost':<15} {'Total Cost':<15}")
    logging.info("-" * 65)
    for model, pricing in costs.items():
        logging.info(f"{model:<20} ${pricing['input_cost_normal']:<14} ${pricing['output_cost_normal']:<14} ${pricing['total_cost_normal']:<14}")
    
    logging.info("\n")
    logging.info(f"{'Model':<20} {'Input Cost (Batch)':<18} {'Output Cost (Batch)':<18} {'Total Cost (Batch)':<18}")
    logging.info("-" * 75)
    for model, pricing in costs.items():
        logging.info(f"{model:<20} ${pricing['input_cost_batch']:<17} ${pricing['output_cost_batch']:<17} ${pricing['total_cost_batch']:<17}")

# -------------------------------
# Main Execution
# -------------------------------

if __name__ == "__main__":
    calculate_costs()
