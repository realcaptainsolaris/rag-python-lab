"""Historical initializer retired after editorial revision 0.1.1.

Edit facts.yaml, pilot_documents.json and question_plan.json directly.
This guard prevents accidental restoration of the superseded 0.1.0 source.
"""
if __name__ == "__main__":
    raise SystemExit("Initializer retired. Rebuild with: python scripts/build_corpus.py")
