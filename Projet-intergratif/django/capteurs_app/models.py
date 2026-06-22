from django.db import models


class Capteur(models.Model):
    id_capteur = models.CharField(max_length=255, primary_key=True)
    nom = models.CharField(max_length=255, unique=True)
    piece = models.CharField(max_length=255)
    emplacement = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'capteurs'

    def __str__(self):
        return self.nom


class Mesure(models.Model):
    id_mesure = models.AutoField(primary_key=True)
    id_capteur = models.ForeignKey(
        Capteur,
        on_delete=models.CASCADE,
        db_column='id_capteur',
    )
    horodatage = models.DateTimeField()
    temperature = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'mesures'

    def __str__(self):
        return f"{self.id_capteur_id} — {self.horodatage} : {self.temperature}°C"
