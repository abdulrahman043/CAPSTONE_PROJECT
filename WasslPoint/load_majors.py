import json
from profiles.models import Major

with open('majors.json', encoding='utf-8') as f:
    data = json.load(f)
for item in data:
    Major.objects.update_or_create(
        en_name=item['en_name'],
        defaults={'ar_name': item['ar_name'], 'status': item['status']}
    )
