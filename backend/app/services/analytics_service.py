"""Historical topic analysis, frequency dashboard metrics, and chronological backtesting."""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.academic import Subject, SyllabusUnit, SyllabusTopic, VerificationStatus
from app.models.question_paper import QuestionPaper, ExtractedQuestion


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_topic_analytics(self, subject_id: int) -> Dict[str, Any]:
        """
        Compute frequency and exam-pattern statistics for each syllabus topic.
        Does NOT represent probability of future appearance, but transparent historical frequency.
        """
        # Fetch all units and topics for the subject
        units = (
            self.db.query(SyllabusUnit)
            .filter(SyllabusUnit.subject_id == subject_id)
            .all()
        )

        total_verified_papers = (
            self.db.query(func.count(QuestionPaper.id))
            .filter(
                QuestionPaper.subject_id == subject_id,
                QuestionPaper.verification_status == VerificationStatus.VERIFIED,
            )
            .scalar() or 0
        )

        topic_stats = []
        for u in units:
            for t in u.topics:
                # Query verified questions mapped to this topic
                q_records = (
                    self.db.query(ExtractedQuestion, QuestionPaper)
                    .join(QuestionPaper, ExtractedQuestion.paper_id == QuestionPaper.id)
                    .filter(
                        ExtractedQuestion.topic_id == t.id,
                        QuestionPaper.verification_status == VerificationStatus.VERIFIED,
                        ExtractedQuestion.is_human_verified == True,
                    )
                    .all()
                )

                appearances = len(q_records)
                distinct_papers = len(set(p.id for q, p in q_records))
                years = [p.exam_year for q, p in q_records]
                most_recent_year = max(years) if years else None
                marks_list = [q.marks for q, p in q_records if q.marks]
                avg_marks = round(sum(marks_list) / len(marks_list), 1) if marks_list else 7.0

                topic_stats.append({
                    "topic_id": t.id,
                    "topic_name": t.topic_name,
                    "unit_number": u.unit_number,
                    "unit_title": u.title,
                    "total_appearances": appearances,
                    "distinct_papers_count": distinct_papers,
                    "eligible_papers_count": total_verified_papers,
                    "paper_frequency_ratio": round(distinct_papers / total_verified_papers, 2) if total_verified_papers > 0 else 0.0,
                    "most_recent_year": most_recent_year,
                    "avg_marks": avg_marks,
                    "importance_level": t.importance_level,
                })

        # Sort by distinct papers count descending
        topic_stats.sort(key=lambda x: (x["distinct_papers_count"], x["total_appearances"]), reverse=True)

        return {
            "subject_id": subject_id,
            "total_verified_papers": total_verified_papers,
            "topics": topic_stats,
            "disclaimer": "Historical frequencies show past appearance patterns and do not guarantee future exam questions.",
        }

    def run_chronological_backtest(
        self,
        subject_id: int,
        target_year: int = 2023,
        k: int = 5
    ) -> Dict[str, Any]:
        """
        Chronological backtesting:
        1. Train/Rank topics using only papers strictly BEFORE target_year.
        2. Ground truth: topics that actually appeared in target_year papers.
        3. Measure Precision@K and Recall@K without future-paper leakage.
        """
        # Historical papers before target year
        prior_questions = (
            self.db.query(ExtractedQuestion)
            .join(QuestionPaper, ExtractedQuestion.paper_id == QuestionPaper.id)
            .filter(
                QuestionPaper.subject_id == subject_id,
                QuestionPaper.exam_year < target_year,
                QuestionPaper.verification_status == VerificationStatus.VERIFIED,
                ExtractedQuestion.is_human_verified == True,
            )
            .all()
        )

        prior_counts: Dict[int, int] = {}
        for q in prior_questions:
            if q.topic_id:
                prior_counts[q.topic_id] = prior_counts.get(q.topic_id, 0) + 1

        # Sort topics by prior frequency (our ranking model)
        ranked_topic_ids = sorted(prior_counts.keys(), key=lambda t: prior_counts[t], reverse=True)
        top_k_predicted = set(ranked_topic_ids[:k])

        # Actual questions that appeared in target year
        actual_target_questions = (
            self.db.query(ExtractedQuestion)
            .join(QuestionPaper, ExtractedQuestion.paper_id == QuestionPaper.id)
            .filter(
                QuestionPaper.subject_id == subject_id,
                QuestionPaper.exam_year == target_year,
                QuestionPaper.verification_status == VerificationStatus.VERIFIED,
                ExtractedQuestion.is_human_verified == True,
            )
            .all()
        )

        actual_topic_ids = set(q.topic_id for q in actual_target_questions if q.topic_id)

        # Calculate metrics
        hits = len(top_k_predicted.intersection(actual_topic_ids))
        precision_at_k = round(hits / k, 3) if k > 0 else 0.0
        recall_at_k = round(hits / len(actual_topic_ids), 3) if actual_topic_ids else 0.0

        return {
            "subject_id": subject_id,
            "backtest_target_year": target_year,
            "k": k,
            "prior_papers_count": len(set(q.paper_id for q in prior_questions)),
            "actual_topics_count": len(actual_topic_ids),
            "hits": hits,
            "precision_at_k": precision_at_k,
            "recall_at_k": recall_at_k,
            "method": "historical_frequency_prior_to_target",
            "leakage_prevented": True,
        }
