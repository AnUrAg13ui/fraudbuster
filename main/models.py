from django.db import models


# Create your models here.
class TrainedModels(models.Model):
    class Meta:
        verbose_name = 'Trained Model'
        verbose_name_plural = 'Trained Models'
    name = models.CharField(max_length=255)
    model = models.BinaryField()
    featured_columns = models.JSONField()
    label_encoders = models.BinaryField(null=True, blank=True)
    scaler = models.BinaryField(null=True, blank=True)
    result = models.BinaryField(null=True, blank=True)
    trained_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name
