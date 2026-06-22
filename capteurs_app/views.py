import csv
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q, Avg

from .models import Capteur, Mesure
from .forms import CapteurEditForm


def liste_capteurs(request):
    capteurs = Capteur.objects.all().order_by('nom')

    search = request.GET.get('search', '').strip()
    if search:
        capteurs = capteurs.filter(
            Q(nom__icontains=search) | Q(id_capteur__icontains=search)
        )

    return render(request, 'capteurs_app/liste_capteurs.html', {
        'capteurs': capteurs,
        'search': search,
    })


def _filtrer_mesures(capteur, date_debut, date_fin):
    """Retourne le queryset des mesures d'un capteur avec les filtres de date appliqués."""
    mesures = Mesure.objects.filter(id_capteur=capteur)
    if date_debut:
        mesures = mesures.filter(horodatage__date__gte=date_debut)
    if date_fin:
        mesures = mesures.filter(horodatage__date__lte=date_fin)
    return mesures


def detail_capteur(request, id_capteur):
    capteur = get_object_or_404(Capteur, pk=id_capteur)

    if request.method == 'POST':
        form = CapteurEditForm(request.POST, instance=capteur)
        if form.is_valid():
            form.save()
            return redirect('capteurs_app:detail_capteur', id_capteur=id_capteur)
    else:
        form = CapteurEditForm(instance=capteur)

    date_debut = request.GET.get('date_debut', '').strip()
    date_fin = request.GET.get('date_fin', '').strip()

    # Queryset filtré, utilisé pour le tableau, la moyenne et le graphique
    mesures = _filtrer_mesures(capteur, date_debut, date_fin).order_by('-horodatage')

    # 1. Température moyenne des mesures affichées
    temp_moyenne = mesures.aggregate(moyenne=Avg('temperature'))['moyenne']

    # 3. Données pour Chart.js — ordre chronologique pour l'axe X
    mesures_chrono = list(
        mesures.order_by('horodatage').values('horodatage', 'temperature')
    )
    chart_labels = json.dumps(
        [m['horodatage'].strftime('%d/%m %H:%M') for m in mesures_chrono]
    )
    chart_data = json.dumps(
        [float(m['temperature']) for m in mesures_chrono]
    )

    return render(request, 'capteurs_app/detail_capteur.html', {
        'capteur': capteur,
        'mesures': mesures,
        'form': form,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'temp_moyenne': temp_moyenne,   # fonctionnalité 1
        'chart_labels': chart_labels,   # fonctionnalité 3
        'chart_data': chart_data,       # fonctionnalité 3
    })


def supprimer_toutes_mesures(request):
    """Supprime toutes les mesures de la base — accessible uniquement en POST."""
    if request.method == 'POST':
        Mesure.objects.all().delete()
    return redirect('capteurs_app:liste_capteurs')


def export_csv(request, id_capteur):
    """Fonctionnalité 2 : export CSV des mesures filtrées par date."""
    capteur = get_object_or_404(Capteur, pk=id_capteur)

    date_debut = request.GET.get('date_debut', '').strip()
    date_fin = request.GET.get('date_fin', '').strip()

    # Même logique de filtrage que detail_capteur, ordre chronologique pour le fichier
    mesures = _filtrer_mesures(capteur, date_debut, date_fin).order_by('horodatage')

    # HttpResponse avec content_type CSV déclenche le téléchargement dans le navigateur
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="mesures_{id_capteur}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(['horodatage', 'temperature'])  # en-tête
    for mesure in mesures:
        writer.writerow([
            mesure.horodatage.strftime('%Y-%m-%d %H:%M:%S'),
            mesure.temperature,
        ])

    return response
