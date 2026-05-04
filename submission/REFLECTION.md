# Reflection

Our team's data would be most at risk of the **Small Files Problem** anti-pattern. 

Since our systems ingest data continuously in micro-batches (e.g., from streaming events or frequent API calls), we constantly append tiny amounts of data to the storage layer. Without a regular compaction strategy (like `OPTIMIZE`), these continuous appends lead to thousands of small files under the hood. As demonstrated in NB2, this drastically slows down query performance because the engine spends more time on file I/O overhead (listing and opening files) than on actual data scanning. 

To mitigate this, we need to enforce periodic `OPTIMIZE` and `ZORDER` operations as part of our pipeline orchestration to merge these small files into larger, more efficient blocks, ensuring that downstream analytics remain performant.
