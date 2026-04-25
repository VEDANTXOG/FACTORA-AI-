from django.db import models
import uuid
from django.db.models import Max, Func, Value, CharField

class NewsAnalysis(models.Model):
    VERDICT_CHOICES = [
        ('REAL', 'REAL'),
        ('FAKE', 'FAKE'),
        ('SUSPICIOUS', 'SUSPICIOUS'),
    ]
    
    id = models.AutoField(primary_key=True)
    news_id = models.CharField(max_length=20, unique=True)
    content = models.TextField()
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES)
    reason = models.TextField()
    sources = models.TextField(blank=True)  # Comma-separated or JSON string
    manipulation_score = models.FloatField()
    verification_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    uid = models.CharField(max_length=36, unique=True, editable=False)
    
    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = str(uuid.uuid4())
        
        if not self.news_id:
            # Generate sequential NEWS001, NEWS002 etc.
            max_id = NewsAnalysis.objects.aggregate(
                max_num=Max(Func(
                    models.F('news_id'),
                    function='SUBSTRING',
                    template="%(function)s(%(expressions)s, 5)",  # After 'NEWS'
                    output_field=CharField()
                ))
            )['max_num']
            next_num = 1 if max_id is None else int(max_id) + 1
            self.news_id = f"NEWS{next_num:03d}"
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.news_id} - {self.verdict}"

