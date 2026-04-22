from app.core.orchestrator import run_pipeline

if __name__ == "__main__":
    run_dir = run_pipeline()
    print(f"Run complete: {run_dir}")
