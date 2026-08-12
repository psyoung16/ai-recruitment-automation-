"""
평가 시스템 (Evaluation)

Ground Truth와 시스템 예측을 비교하여 정확도를 측정합니다.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import argparse


@dataclass
class GroundTruth:
    """Ground Truth 데이터"""
    job_id: str
    label: str  # apply, borderline, no_apply
    expected_score: Optional[int]
    company: str
    position: str


@dataclass
class Prediction:
    """시스템 예측 데이터"""
    job_id: str
    score: int
    recommended: bool
    model: str


@dataclass
class JobEvaluation:
    """개별 공고 평가 결과"""
    job_id: str
    company: str
    ground_truth_label: str
    ground_truth_score: Optional[int]
    predicted_label: str  # apply or no_apply
    predicted_score: int
    predicted_recommended: bool
    correct: bool
    error_type: Optional[str]  # false_positive, false_negative, true_positive, true_negative
    score_error: Optional[float]
    model: str


class EvaluationReport:
    """평가 결과 리포트"""

    def __init__(self, query: str, model_name: str = "gemini-3.6-flash"):
        self.query = query
        self.model_name = model_name
        self.timestamp = datetime.now()
        self.evaluation_id = f"eval_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"

        self.detailed_results: List[JobEvaluation] = []
        self.summary: Dict = {}
        self.confusion_matrix: Dict = {}
        self.failure_cases: List[Dict] = []

    def add_result(self, result: JobEvaluation):
        """평가 결과 추가"""
        self.detailed_results.append(result)

    def calculate_metrics(self):
        """메트릭 계산"""
        if not self.detailed_results:
            return

        # 기본 통계
        total = len(self.detailed_results)
        correct = sum(1 for r in self.detailed_results if r.correct)

        # Confusion Matrix 계산 (borderline 제외)
        evaluated = [r for r in self.detailed_results if r.ground_truth_label != 'borderline']

        tp = sum(1 for r in evaluated if r.error_type == 'true_positive')
        fp = sum(1 for r in evaluated if r.error_type == 'false_positive')
        tn = sum(1 for r in evaluated if r.error_type == 'true_negative')
        fn = sum(1 for r in evaluated if r.error_type == 'false_negative')

        # Precision, Recall, F1
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        # MAE 계산 (점수 있는 것만)
        score_errors = [r.score_error for r in self.detailed_results if r.score_error is not None]
        mae = sum(score_errors) / len(score_errors) if score_errors else None

        # Summary
        self.summary = {
            "total_jobs": total,
            "evaluated_jobs": len(evaluated),  # borderline 제외
            "borderline_excluded": total - len(evaluated),
            "accuracy": correct / len(evaluated) if evaluated else 0,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "mae": mae,
            "apply_count": sum(1 for r in self.detailed_results if r.ground_truth_label == 'apply'),
            "borderline_count": sum(1 for r in self.detailed_results if r.ground_truth_label == 'borderline'),
            "no_apply_count": sum(1 for r in self.detailed_results if r.ground_truth_label == 'no_apply'),
        }

        # Confusion Matrix
        self.confusion_matrix = {
            "true_positive": tp,
            "false_positive": fp,
            "true_negative": tn,
            "false_negative": fn
        }

        # Failure Cases
        self.failure_cases = [
            {
                "job_id": r.job_id,
                "company": r.company,
                "error_type": r.error_type,
                "ground_truth": r.ground_truth_label,
                "predicted": "apply" if r.predicted_recommended else "no_apply",
                "ground_truth_score": r.ground_truth_score,
                "predicted_score": r.predicted_score,
                "score_diff": r.predicted_score - r.ground_truth_score if r.ground_truth_score else None
            }
            for r in self.detailed_results
            if not r.correct and r.ground_truth_label != 'borderline'
        ]

    def to_json(self) -> dict:
        """JSON 직렬화"""
        return {
            "metadata": {
                "evaluation_id": self.evaluation_id,
                "timestamp": self.timestamp.isoformat(),
                "query": self.query,
                "model_name": self.model_name,
            },
            "summary": self.summary,
            "confusion_matrix": self.confusion_matrix,
            "detailed_results": [asdict(r) for r in self.detailed_results],
            "failure_cases": self.failure_cases
        }

    def save_json(self, output_dir: str):
        """JSON 파일로 저장"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 1. 평가 결과 JSON 저장
        json_file = output_path / f"{self.evaluation_id}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.to_json(), f, ensure_ascii=False, indent=2)

        # 2. latest.json 심볼릭 링크 (최신 결과)
        latest_file = output_path / "latest.json"
        if latest_file.exists():
            latest_file.unlink()

        # 상대 경로로 심볼릭 링크 생성
        try:
            latest_file.symlink_to(json_file.name)
        except OSError:
            # Windows에서 심볼릭 링크 실패 시 복사
            import shutil
            shutil.copy(json_file, latest_file)

        return json_file

    def save_markdown(self, output_dir: str):
        """마크다운 리포트 저장"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        md_file = output_path / f"{self.evaluation_id}.md"

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(self._to_markdown())

        return md_file

    def _to_markdown(self) -> str:
        """마크다운 포맷"""
        s = self.summary
        cm = self.confusion_matrix

        md = f"""# 📊 Evaluation Report

## Metadata
- **Evaluation ID**: {self.evaluation_id}
- **Date**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
- **Query**: {self.query}
- **Model**: {self.model_name}

---

## 📈 Summary

| Metric | Value |
|--------|-------|
| **Total Jobs** | {s['total_jobs']} |
| **Evaluated** | {s['evaluated_jobs']} (borderline {s['borderline_excluded']}개 제외) |
| **Accuracy** | {s['accuracy']:.1%} ({int(s['accuracy'] * s['evaluated_jobs'])}/{s['evaluated_jobs']}) |
| **Precision** | {s['precision']:.1%} |
| **Recall** | {s['recall']:.1%} |
| **F1-Score** | {s['f1_score']:.3f} |
| **MAE** | {s['mae']:.1f}점 (평균 점수 오차) |

### Ground Truth Distribution
- ✅ apply: {s['apply_count']}개
- ⚠️ borderline: {s['borderline_count']}개
- ❌ no_apply: {s['no_apply_count']}개

---

## 🎯 Confusion Matrix

|  | Predicted: apply | Predicted: no_apply |
|--|------------------|---------------------|
| **Actual: apply** | ✅ TP: {cm['true_positive']} | ❌ FN: {cm['false_negative']} |
| **Actual: no_apply** | ⚠️ FP: {cm['false_positive']} | ✅ TN: {cm['true_negative']} |

- **True Positive (TP)**: 실제 apply, 예측 apply ✅
- **False Positive (FP)**: 실제 no_apply, 예측 apply ⚠️ **(치명적!)**
- **True Negative (TN)**: 실제 no_apply, 예측 no_apply ✅
- **False Negative (FN)**: 실제 apply, 예측 no_apply ❌

---

## 🔍 Failure Cases

"""

        if self.failure_cases:
            for i, case in enumerate(self.failure_cases, 1):
                md += f"""
### {i}. Job {case['job_id']} - {case['company']} ({case['error_type'].upper()})
- **Ground Truth**: {case['ground_truth']}
- **Predicted**: {case['predicted']}
- **Score**: GT={case['ground_truth_score']} vs Pred={case['predicted_score']} (차이: {case['score_diff']:+d}점)
"""
        else:
            md += "\n✅ **모든 케이스 정확!** (failure case 없음)\n"

        md += "\n---\n\n## 📋 Detailed Results\n\n"
        md += "| Job ID | Company | GT Label | Pred | Score (GT/Pred) | Correct | Error Type |\n"
        md += "|--------|---------|----------|------|-----------------|---------|------------|\n"

        for r in self.detailed_results:
            correct_mark = "✅" if r.correct else "❌"
            gt_score = r.ground_truth_score if r.ground_truth_score else "-"
            error_type = r.error_type if r.error_type else "-"
            pred_label = "apply" if r.predicted_recommended else "no_apply"

            md += f"| {r.job_id} | {r.company} | {r.ground_truth_label} | {pred_label} | {gt_score}/{r.predicted_score} | {correct_mark} | {error_type} |\n"

        return md

    def print_summary(self):
        """콘솔에 요약 출력"""
        s = self.summary
        cm = self.confusion_matrix

        print("\n" + "=" * 70)
        print(f"📊 Evaluation Report - {self.evaluation_id}")
        print("=" * 70)
        print(f"\n📅 Date: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔍 Query: {self.query}")
        print(f"🤖 Model: {self.model_name}")

        print("\n" + "-" * 70)
        print("📈 Summary")
        print("-" * 70)
        print(f"Total Jobs:      {s['total_jobs']}")
        print(f"Evaluated:       {s['evaluated_jobs']} (borderline {s['borderline_excluded']}개 제외)")
        print(f"\nAccuracy:        {s['accuracy']:.1%} ({int(s['accuracy'] * s['evaluated_jobs'])}/{s['evaluated_jobs']})")
        print(f"Precision:       {s['precision']:.1%}")
        print(f"Recall:          {s['recall']:.1%}")
        print(f"F1-Score:        {s['f1_score']:.3f}")
        if s['mae']:
            print(f"MAE:             {s['mae']:.1f}점")

        print("\n" + "-" * 70)
        print("🎯 Confusion Matrix")
        print("-" * 70)
        print(f"True Positive:   {cm['true_positive']} ✅")
        print(f"False Positive:  {cm['false_positive']} ⚠️  (잘못 추천)")
        print(f"True Negative:   {cm['true_negative']} ✅")
        print(f"False Negative:  {cm['false_negative']} ❌ (놓친 공고)")

        if self.failure_cases:
            print("\n" + "-" * 70)
            print("🔍 Failure Cases")
            print("-" * 70)
            for i, case in enumerate(self.failure_cases, 1):
                print(f"\n{i}. Job {case['job_id']} - {case['company']}")
                print(f"   Error Type: {case['error_type'].upper()}")
                print(f"   GT: {case['ground_truth']} / Pred: {case['predicted']}")
                print(f"   Score: {case['ground_truth_score']} → {case['predicted_score']} ({case['score_diff']:+d}점)")

        print("\n" + "=" * 70)


def load_ground_truth(test_jobs_file: str) -> List[GroundTruth]:
    """Ground Truth 로드"""
    with open(test_jobs_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ground_truths = []

    for job in data.get('apply', []):
        ground_truths.append(GroundTruth(
            job_id=job['job_id'],
            label='apply',
            expected_score=job.get('my_expected_score'),
            company=job['company'],
            position=job['position']
        ))

    for job in data.get('borderline', []):
        ground_truths.append(GroundTruth(
            job_id=job['job_id'],
            label='borderline',
            expected_score=job.get('my_expected_score'),
            company=job['company'],
            position=job['position']
        ))

    for job in data.get('no_apply', []):
        ground_truths.append(GroundTruth(
            job_id=job['job_id'],
            label='no_apply',
            expected_score=job.get('my_expected_score'),
            company=job['company'],
            position=job['position']
        ))

    return ground_truths


def load_predictions(output_dir: str, query: str) -> Dict[str, Prediction]:
    """시스템 예측 로드"""
    predictions = {}
    output_path = Path(output_dir) / query

    if not output_path.exists():
        return predictions

    for file in output_path.glob("job_*_analyzed.json"):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)

            job_id = data['job_id']
            predictions[job_id] = Prediction(
                job_id=job_id,
                score=data['match_result']['score'],
                recommended=data['recommended'],
                model=data.get('model', 'unknown')
            )

    return predictions


def evaluate(ground_truths: List[GroundTruth], predictions: Dict[str, Prediction], query: str) -> EvaluationReport:
    """평가 실행"""
    report = EvaluationReport(query=query)

    for gt in ground_truths:
        pred = predictions.get(gt.job_id)

        if not pred:
            print(f"⚠️  Warning: Job {gt.job_id} not found in predictions (skipping)")
            continue

        # 예측 라벨 (recommended 기준)
        predicted_label = 'apply' if pred.recommended else 'no_apply'

        # 정답 여부 판단
        if gt.label == 'borderline':
            # borderline은 정답/오답 판단하지 않음 (참고용)
            correct = None
            error_type = 'borderline'
        else:
            # apply vs no_apply만 평가
            gt_binary = 'apply' if gt.label == 'apply' else 'no_apply'
            correct = (gt_binary == predicted_label)

            # Error Type 분류
            if gt_binary == 'apply' and predicted_label == 'apply':
                error_type = 'true_positive'
            elif gt_binary == 'apply' and predicted_label == 'no_apply':
                error_type = 'false_negative'
            elif gt_binary == 'no_apply' and predicted_label == 'apply':
                error_type = 'false_positive'
            else:  # no_apply -> no_apply
                error_type = 'true_negative'

        # 점수 오차
        score_error = None
        if gt.expected_score is not None:
            score_error = abs(pred.score - gt.expected_score)

        result = JobEvaluation(
            job_id=gt.job_id,
            company=gt.company,
            ground_truth_label=gt.label,
            ground_truth_score=gt.expected_score,
            predicted_label=predicted_label,
            predicted_score=pred.score,
            predicted_recommended=pred.recommended,
            correct=correct if correct is not None else True,  # borderline은 True로 처리
            error_type=error_type,
            score_error=score_error,
            model=pred.model
        )

        report.add_result(result)

    report.calculate_metrics()
    return report


def main():
    parser = argparse.ArgumentParser(description="평가 시스템")
    parser.add_argument(
        "--query",
        type=str,
        default="백엔드-eval",
        help="평가할 쿼리 (기본: 백엔드-eval)"
    )
    parser.add_argument(
        "--test-jobs",
        type=str,
        default="evaluation/test_jobs.json",
        help="Ground Truth 파일 경로"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="예측 결과 디렉토리"
    )
    parser.add_argument(
        "--report-dir",
        type=str,
        default="evaluation/reports",
        help="리포트 저장 디렉토리"
    )

    args = parser.parse_args()

    # 1. Ground Truth 로드
    print(f"📂 Loading Ground Truth from {args.test_jobs}...")
    ground_truths = load_ground_truth(args.test_jobs)
    print(f"✅ Loaded {len(ground_truths)} jobs")

    # 2. 예측 결과 로드
    print(f"\n📂 Loading Predictions from {args.output_dir}/{args.query}...")
    predictions = load_predictions(args.output_dir, args.query)
    print(f"✅ Loaded {len(predictions)} predictions")

    if not predictions:
        print("\n❌ Error: No predictions found!")
        print(f"먼저 분석을 실행하세요: python batch_matcher.py --query \"{args.query}\"")
        sys.exit(1)

    # 3. 평가 실행
    print(f"\n🔍 Evaluating...")
    report = evaluate(ground_truths, predictions, args.query)

    # 4. 결과 저장
    json_file = report.save_json(args.report_dir)
    md_file = report.save_markdown(args.report_dir)

    print(f"\n✅ JSON report saved: {json_file}")
    print(f"✅ Markdown report saved: {md_file}")

    # 5. 콘솔 출력
    report.print_summary()

    print(f"\n💡 Tip: 상세 결과는 {md_file} 참고")


if __name__ == "__main__":
    main()
