import os
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall
from datasets import Dataset

def run_evaluation():
    # Example dataset structure needed by RAGAS
    data = {
        "question": ["Who is the CEO of Apple?"],
        "answer": ["Tim Cook is the CEO of Apple."],
        "contexts": [["Tim Cook, also known as Timothy D. Cook, leads Apple as its CEO."]],
        "ground_truths": [["Tim Cook is the CEO of Apple."]]
    }
    
    dataset = Dataset.from_dict(data)
    
    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_recall,
        ],
    )
    
    print("Evaluation Results:", result)

if __name__ == "__main__":
    # Ensure OPENAI_API_KEY is set in environment for RAGAS LLM evaluations
    run_evaluation()
