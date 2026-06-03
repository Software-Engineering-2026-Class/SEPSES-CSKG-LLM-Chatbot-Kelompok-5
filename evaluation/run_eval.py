"""
SEPSES CSKG LLM Chatbot - Evaluation CLI Runner
================================================
Tanggung Jawab  : Satya Wira Pramudita (Evaluator & Log Dev)
Branch          : feature/eval-log-dev

Penggunaan:
    python evaluation/run_eval.py --llm openai/gpt-4o-mini google/gemini-flash-latest --category all
    python evaluation/run_eval.py --llm openai/gpt-4o-mini --category kg_qa --output ./results/

Catatan:
    Script ini memerlukan RAG pipeline (rag_logic/) sudah siap.
    Hubungi Fahmi Abdillah Zain untuk dependency rag_logic.rag_pipeline.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Tuple

import structlog
from dotenv import load_dotenv

load_dotenv()

# Tambah root project ke sys.path agar import bekerja
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.grader import EvalResult, EvalSummary, Grader

logger = structlog.get_logger(__name__)

# ============================================================
# LLM Name Constants (OpenRouter format)
# ============================================================
# Default models for evaluation - can be overridden via CLI
DEFAULT_MODELS = [
    "openai/gpt-4o-mini",           # OpenAI GPT-4o mini
    "google/gemini-flash-latest",   # Google Gemini Flash (latest)
]

# Legacy name mapping for backward compatibility
LEGACY_MODEL_MAPPING = {
    "gpt4o-mini": "openai/gpt-4o-mini",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "mistral": "mistralai/mistral-7b-instruct",
    "gemini": "google/gemini-flash-latest",
}


def _get_mock_answer_generator(llm_name: str):
    """
    Generator jawaban mock untuk testing tanpa RAG pipeline aktif.

    CATATAN: Ini adalah PLACEHOLDER yang harus diganti dengan
    pemanggilan rag_logic.rag_pipeline.RagPipeline(llm_name=llm_name).query()
    setelah Fahmi menyelesaikan modul rag_logic.

    Args:
        llm_name: Nama LLM.

    Returns:
        Callable: Fungsi yang menerima question dan return (answer, context, latency_ms).
    """
    def generate(question: str) -> Tuple[str, str, float]:
        """
        Mock answer generator.

        Args:
            question: Pertanyaan dalam natural language.

        Returns:
            Tuple[str, str, float]: (answer, context, latency_ms)
        """
        start = time.time()
        # Placeholder - akan diganti dengan actual RAG pipeline call
        mock_answer = (
            f"[MOCK - {llm_name}] This is a placeholder answer for evaluation testing. "
            f"Question: {question[:100]}..."
        )
        mock_context = "[MOCK CONTEXT] No real KG or log context retrieved in mock mode."
        latency_ms = (time.time() - start) * 1000
        return mock_answer, mock_context, latency_ms

    return generate


def _get_real_answer_generator(llm_name: str):
    """
    Generator jawaban nyata menggunakan RAG pipeline.

    Args:
        llm_name: Nama LLM yang akan digunakan.

    Returns:
        Callable: Fungsi question -> (answer, context, latency_ms).

    Raises:
        ImportError: Jika rag_logic belum tersedia.
    """
    try:
        from rag_logic.rag_pipeline import RagPipeline  # type: ignore
        pipeline = RagPipeline(llm_name=llm_name)

        def generate(question: str) -> Tuple[str, str, float]:
            """
            Generate answer via RAG pipeline.

            Args:
                question: Pertanyaan dalam natural language.

            Returns:
                Tuple[str, str, float]: (answer, context, latency_ms).
            """
            start = time.time()
            result = pipeline.query(question)
            latency_ms = (time.time() - start) * 1000
            return (
                result.get("answer", ""),
                result.get("context", ""),
                latency_ms
            )

        return generate

    except ImportError:
        logger.warning(
            "rag_pipeline_not_available",
            message="rag_logic.rag_pipeline belum tersedia. Menggunakan mock generator.",
            llm=llm_name
        )
        return _get_mock_answer_generator(llm_name)


def print_summary_table(summaries: List[EvalSummary]) -> None:
    """
    Tampilkan tabel perbandingan hasil evaluasi di terminal.

    Args:
        summaries: Daftar EvalSummary per LLM.
    """
    print("\n" + "=" * 70)
    print("  HASIL EVALUASI - SEPSES CSKG LLM CHATBOT")
    print("=" * 70)
    print(f"{'Metric':<30} " + " ".join(f"{s.llm_name:>15}" for s in summaries))
    print("-" * 70)

    metrics = [
        ("Faithfulness", "avg_faithfulness"),
        ("Answer Relevancy", "avg_answer_relevancy"),
        ("Context Precision", "avg_context_precision"),
        ("Overall Score", "avg_overall_score"),
        ("Avg Latency (ms)", "avg_latency_ms"),
        ("Errors", "error_count"),
    ]

    for label, attr in metrics:
        values = [getattr(s, attr) for s in summaries]
        print(f"  {label:<28} " + " ".join(f"{v:>15.4f}" for v in values))

    print("=" * 70)

    # Per-kategori breakdown
    print("\n  BREAKDOWN PER KATEGORI:")
    print("-" * 70)
    all_categories = set()
    for s in summaries:
        all_categories.update(s.results_by_category.keys())

    for cat in sorted(all_categories):
        print(f"\n  [{cat.upper()}]")
        for s in summaries:
            cat_data = s.results_by_category.get(cat, {})
            overall = cat_data.get("avg_overall", 0.0)
            count = cat_data.get("count", 0)
            print(f"    {s.llm_name:<20}: Overall={overall:.4f} (n={count})")

    print("\n" + "=" * 70)


def main() -> None:
    """
    Entry point CLI untuk menjalankan evaluasi batch.

    Raises:
        SystemExit: Jika argumen tidak valid.
    """
    parser = argparse.ArgumentParser(
        description="SEPSES CSKG LLM Chatbot - Automated Evaluation Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh:
  python evaluation/run_eval.py --llm openai/gpt-4o-mini google/gemini-flash-latest
  python evaluation/run_eval.py --llm openai/gpt-4o-mini --category kg_qa
  python evaluation/run_eval.py --llm anthropic/claude-3.5-sonnet --mock --output ./evaluation/results/

Model format: provider/model-name (OpenRouter format)
Contoh model: openai/gpt-4o-mini, google/gemini-flash-latest, anthropic/claude-3.5-sonnet
Legacy names (gpt4o-mini, mistral) juga didukung untuk backward compatibility.
        """
    )

    parser.add_argument(
        "--llm",
        nargs="+",
        required=True,
        help=(
            "LLM yang akan dievaluasi dalam format OpenRouter (provider/model-name). "
            f"Contoh: {', '.join(DEFAULT_MODELS)}. "
            "Lihat https://openrouter.ai/models untuk daftar lengkap. "
            "Legacy names juga didukung untuk backward compatibility."
        )
    )
    parser.add_argument(
        "--category",
        default="all",
        choices=["all", "security_analysis", "log_analysis", "kg_qa"],
        help="Filter kategori pertanyaan (default: all)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Direktori output untuk hasil evaluasi (default dari .env EVAL_RESULTS_DIR)"
    )
    parser.add_argument(
        "--benchmark",
        default=None,
        help="Path ke benchmark dataset JSON (default: evaluation/benchmark_dataset.json)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Gunakan mock answer generator (tanpa RAG pipeline aktif, untuk testing)"
    )
    parser.add_argument(
        "--judge-model",
        default=None,
        help="Model judge yang digunakan (default dari .env JUDGE_MODEL)"
    )

    args = parser.parse_args()

    logger.info(
        "evaluation_start",
        llms=args.llm,
        category=args.category,
        mock_mode=args.mock
    )

    # Init Grader
    try:
        grader = Grader(
            benchmark_path=args.benchmark,
            results_dir=args.output,
            judge_model=args.judge_model,
        )
    except (FileNotFoundError, ValueError) as exc:
        logger.error("grader_init_failed", error=str(exc))
        print(f"\n❌ ERROR: {exc}")
        sys.exit(1)

    # Jalankan evaluasi per LLM
    all_results = {}
    summaries = []

    for llm_name in args.llm:
        # Map legacy model names to OpenRouter format
        original_name = llm_name
        if llm_name.lower() in LEGACY_MODEL_MAPPING:
            llm_name = LEGACY_MODEL_MAPPING[llm_name.lower()]
            logger.info("legacy_model_mapped", original=original_name, mapped=llm_name)

        print(f"\n🔄 Evaluating: {llm_name} ...")

        # Pilih answer generator
        if args.mock:
            generator_fn = _get_mock_answer_generator(llm_name)
        else:
            generator_fn = _get_real_answer_generator(llm_name)

        # Batch evaluation
        category_filter = None if args.category == "all" else args.category
        results = grader.evaluate_batch(
            llm_name=llm_name,
            answer_generator_fn=generator_fn,
            category_filter=category_filter,
        )
        all_results[llm_name] = results

        # Hitung summary
        summary = grader.compute_summary(results)
        summaries.append(summary)
        print(f"  ✅ {llm_name}: Overall Score = {summary.avg_overall_score:.4f}")

    # Tampilkan tabel perbandingan
    print_summary_table(summaries)

    # Simpan hasil
    output_path = grader.save_results(all_results, summaries)
    print(f"\n💾 Hasil disimpan ke: {output_path}")
    print(f"   CSV summary   : {output_path.replace('.json', '_summary.csv')}")


if __name__ == "__main__":
    main()
