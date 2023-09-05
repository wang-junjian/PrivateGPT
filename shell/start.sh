# Check File Deduplication
echo "🚗 Start Redis(Check File Deduplication)"
docker run --name redis -d -p 6379:6379 -v $(pwd)/storage/vectorstore/deduplication:/data redis redis-server --save 60 1