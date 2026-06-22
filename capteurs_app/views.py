from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
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


def detail_capteur(request, id_capteur):
    capteur = get_object_or_404(Capteur, pk=id_capteur)

    if request.method == 'POST':
        form = CapteurEditForm(request.POST, instance=capteur)
        if form.is_valid():
            form.save()
            return redirect('capteurs_app:detail_capteur', id_capteur=id_capteur)
    else:
        form = CapteurEditForm(instance=capteur)

    mesures = Mesure.objects.filter(id_capteur=capteur).order_by('-horodatage')

    date_debut = request.GET.get('date_debut', '').strip()
    date_fin = request.GET.get('date_fin', '').strip()

    if date_debut:
        mesures = mesures.filter(horodatage__date__gte=date_debut)
    if date_fin:
        mesures = mesures.filter(horodatage__date__lte=date_fin)

    return render(request, 'capteurs_app/detail_capteur.html', {
        'capteur': capteur,
        'mesures': mesures,
        'form': form,
        'date_debut': date_debut,
        'date_fin': date_fin,
    })
