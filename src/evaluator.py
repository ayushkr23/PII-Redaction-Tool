import json
from collections import defaultdict
from detectors import PIIDetector

def compute_overlap(start1, end1, start2, end2):
    return max(0, min(end1, end2) - max(start1, start2))

def evaluate():
    with open("evaluation/ground_truth.json", "r", encoding="utf-8") as f:
        ground_truth = json.load(f)
        
    detector = PIIDetector()
    
    categories = [
        "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "ORGANIZATION", 
        "ADDRESS", "US_SSN", "CREDIT_CARD", "DATE_OF_BIRTH", "IP_ADDRESS"
    ]
    
    metrics = {cat: {"TP": 0, "FP": 0, "FN": 0} for cat in categories}
    overall = {"TP": 0, "FP": 0, "FN": 0}
    
    # Character level metrics for Accuracy
    total_chars = 0
    tp_chars = 0
    fp_chars = 0
    fn_chars = 0

    false_positives = []
    false_negatives = []
    
    for item in ground_truth:
        text = item["text"]
        total_chars += len(text)
        gt_entities = item["entities"]
        
        predictions = detector.detect(text)
        
        # We need to map which gt_entity was found
        gt_found = [False] * len(gt_entities)
        
        for pred in predictions:
            cat = pred["entity_type"]
            # To be robust, some categories might map differently, but we assume exact category match
            if cat not in categories:
                continue
                
            # Check if this prediction overlaps with a ground truth of the same category
            matched = False
            best_overlap = 0
            best_idx = -1
            
            for i, gt in enumerate(gt_entities):
                if gt["entity_type"] == cat:
                    overlap = compute_overlap(pred["start"], pred["end"], gt["start"], gt["end"])
                    if overlap > 0 and overlap > best_overlap:
                        best_overlap = overlap
                        best_idx = i
                        matched = True
                        
            if matched:
                metrics[cat]["TP"] += 1
                overall["TP"] += 1
                gt_found[best_idx] = True
                tp_chars += best_overlap
                fp_chars += (pred["end"] - pred["start"]) - best_overlap
            else:
                metrics[cat]["FP"] += 1
                overall["FP"] += 1
                fp_chars += (pred["end"] - pred["start"])
                false_positives.append({
                    "text": pred["text"],
                    "category": cat,
                    "context": text
                })
                
        # Any GT not found is FN
        for i, gt in enumerate(gt_entities):
            if not gt_found[i]:
                cat = gt["entity_type"]
                metrics[cat]["FN"] += 1
                overall["FN"] += 1
                fn_chars += (gt["end"] - gt["start"])
                false_negatives.append({
                    "text": gt["text"],
                    "category": cat,
                    "context": text
                })
                
    # Calculate TN chars
    tn_chars = max(0, total_chars - tp_chars - fp_chars - fn_chars)
    accuracy = (tp_chars + tn_chars) / total_chars if total_chars > 0 else 0
    
    def calc_metrics(tp, fp, fn):
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        return precision, recall, f1
        
    report = "# Evaluation Report\n\n"
    report += "## Overall Metrics (Entity Level)\n"
    p, r, f1 = calc_metrics(overall["TP"], overall["FP"], overall["FN"])
    report += f"- **Precision:** {p:.4f}\n"
    report += f"- **Recall:** {r:.4f}\n"
    report += f"- **F1-Score:** {f1:.4f}\n"
    report += f"- **TP:** {overall['TP']}, **FP:** {overall['FP']}, **FN:** {overall['FN']}\n\n"
    
    report += "## Character-Level Accuracy\n"
    report += f"- **Accuracy:** {accuracy:.4f}\n"
    report += f"- **Total Chars:** {total_chars}\n\n"
    
    report += "## Per-Category Results\n"
    for cat in categories:
        m = metrics[cat]
        p, rec, f1 = calc_metrics(m["TP"], m["FP"], m["FN"])
        report += f"### {cat}\n"
        report += f"- Precision: {p:.4f} | Recall: {rec:.4f} | F1: {f1:.4f}\n"
        report += f"- TP: {m['TP']} | FP: {m['FP']} | FN: {m['FN']}\n"
        if m['TP'] == 0 and m['FP'] == 0 and m['FN'] == 0:
            report += "- *No ground-truth instances found in sample.* \n"
        report += "\n"
        
    report += "## False Positives (Sample)\n"
    for fp in false_positives[:10]:
        report += f"- `{fp['text']}` classified as `{fp['category']}` in context: *{fp['context']}*\n"
        
    report += "\n## False Negatives (Sample)\n"
    for fn in false_negatives[:10]:
        report += f"- Missed `{fn['text']}` of type `{fn['category']}` in context: *{fn['context']}*\n"
        
    with open("evaluation/evaluation_report.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    print("Evaluation completed. Report saved to evaluation/evaluation_report.md")

if __name__ == "__main__":
    evaluate()
