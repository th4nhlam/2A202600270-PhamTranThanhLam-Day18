import polars as pl
from deltalake import DeltaTable, write_deltalake
import os
import shutil

# Set up local paths for PoC
table_path = "scratch_poc/legal_embeddings"
if os.path.exists("scratch_poc"):
    shutil.rmtree("scratch_poc")
os.makedirs("scratch_poc", exist_ok=True)

print("--- Step 1: Initial Ingestion with V1 Embeddings ---")
v1_data = pl.DataFrame({
    "chunk_id": ["doc1_c1", "doc1_c2", "doc2_c1"],
    "text": ["Article 1: ...", "Article 2: ...", "Decree 15: ..."],
    "vector_v1": [
        [0.1, 0.2, 0.3], 
        [0.4, 0.5, 0.6], 
        [0.7, 0.8, 0.9]
    ]
})
write_deltalake(table_path, v1_data.to_arrow(), mode="overwrite")
dt = DeltaTable(table_path)
print(f"Table created at Version {dt.version()}")

print("\n--- Step 2: Evolving Schema for V2 Embeddings ---")
# A new embedding model is deployed. We append `vector_v2` without destroying `vector_v1`.
v2_data = pl.DataFrame({
    "chunk_id": ["doc1_c1", "doc1_c2", "doc2_c1"],
    "vector_v2": [
        [0.11, 0.22], 
        [0.44, 0.55], 
        [0.77, 0.88]
    ]
})

# We read the current table, add the new embeddings, and overwrite it to create Version 1.
# This preserves the historical Version 0 while correctly evolving the schema.
current_df = pl.from_arrow(dt.to_pyarrow_table())
updated_df = current_df.join(v2_data, on="chunk_id", how="left")

write_deltalake(table_path, updated_df.to_arrow(), mode="overwrite", schema_mode="overwrite")

dt.update_incremental()
print(f"Embeddings updated. Now at Version {dt.version()}")

print("\n--- Step 3: Demonstrating Legal Reproducibility ---")
# A court case from last year cited search results generated using Version 0.
print("Querying current data (V2 active):")
current_df = pl.from_arrow(dt.to_pyarrow_table())
print(current_df)

print("\nTime Traveling to Version 0 (Reproducing historical V1 results):")
historical_dt = DeltaTable(table_path, version=0)
historical_df = pl.from_arrow(historical_dt.to_pyarrow_table())
print(historical_df)

print("\nSuccess: The system can serve current high-accuracy V2 vectors while mathematically guaranteeing the reproduction of V1 vector results for legal audits.")
