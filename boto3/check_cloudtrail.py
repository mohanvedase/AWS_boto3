import boto3
from collections import Counter
from datetime import datetime, timedelta, timezone

# Setup
cloudtrail = boto3.client('cloudtrail')
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=1)

events = []
token = None

# Fetch events
while True:
    response = cloudtrail.lookup_events(
        StartTime=start_time,
        EndTime=end_time,
        MaxResults=50,
        NextToken=token
    ) if token else cloudtrail.lookup_events(
        StartTime=start_time,
        EndTime=end_time,
        MaxResults=50
    )

    events.extend(response['Events'])
    token = response.get('NextToken')
    if not token:
        break

# Count event types
event_names = [event['EventName'] for event in events]
counter = Counter(event_names)

# Print top 10 event types
for event_name, count in counter.most_common(10):
    print(f"{event_name}: {count} events")
