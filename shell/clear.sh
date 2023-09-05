# Check File Deduplication
echo "🚗 Clearing Redis(Check File Deduplication)"
docker rm -f redis
rm -rf storage/deduplication

# VectorStore
echo "🚗 Clearing VectorStore"
rm -rf storage/vectorstore

# Uploaded Files
echo "🚗 Clearing Uploaded Files"
rm -rf storage/uploaded_files
