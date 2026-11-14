from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required as django_login_required
from django.db import IntegrityError, transaction
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST
from accounts.models import Profile
from accounts.views import get_user_profile, is_ajax
from .models import Friendship, GameInvitation
from .services import get_friends

LEVEL_NAMES = {
    messages.SUCCESS: "success",
    messages.INFO: "info",
    messages.ERROR: "error",
}

SUGGESTION_LIMIT = 8

SEND_OUTCOMES = {
    "sent": (messages.SUCCESS, "Demande d'ami envoyée à {pseudonym}.", Friendship.SENT),
    "accepted": (
        messages.SUCCESS,
        "{pseudonym} vous avait déjà envoyé une demande : vous êtes maintenant amis !",
        Friendship.FRIENDS,
    ),
    "already_sent": (messages.INFO, "Vous avez déjà envoyé une demande à {pseudonym}.", Friendship.SENT),
    "already_friends": (messages.INFO, "Vous êtes déjà ami avec {pseudonym}.", Friendship.FRIENDS),
}


def redirect_back(request):
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect("friends:list")


def login_required(view):
    """Comme `login_required`, mais répond en JSON (401) aux requêtes AJAX
    au lieu de rediriger vers la page de connexion."""
    protected = django_login_required(view)

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated and is_ajax(request):
            return JsonResponse(
                {
                    "success": False,
                    "level": "error",
                    "message": "Votre session a expiré. Veuillez vous reconnecter.",
                },
                status=401,
            )
        return protected(request, *args, **kwargs)

    return wrapper


def respond(request, level, message, success=True):
    """Réponse JSON pour AJAX, sinon message flash + redirection."""
    if is_ajax(request):
        return JsonResponse(
            {"success": success, "level": LEVEL_NAMES.get(
                level, "info"), "message": message}
        )
    messages.add_message(request, level, message)
    return redirect_back(request)


@login_required
def friends_list(request):
    me = request.user
    get_user_profile(me)

    friends = get_friends(me)

    received = Friendship.objects.filter(
        to_user=me, status=Friendship.PENDING
    ).select_related("from_user__profile")

    sent = Friendship.objects.filter(
        from_user=me, status=Friendship.PENDING
    ).select_related("to_user__profile")

    context = {"friends": friends, "received": received, "sent": sent}
    return render(request, "friends/friends.html", context)


@login_required
@require_GET
def search_users(request):
    me = request.user
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"results": []})

    profiles = list(
        Profile.objects.filter(pseudonym__icontains=query)
        .exclude(user=me)
        .annotate(
            rank=Case(
                When(pseudonym__istartswith=query, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by("rank", "pseudonym")[:SUGGESTION_LIMIT]
    )

    ids = [p.user_id for p in profiles]
    links = Friendship.objects.filter(
        Q(from_user=me, to_user_id__in=ids) | Q(
            to_user=me, from_user_id__in=ids)
    )
    statuses = {
        (link.to_user_id if link.from_user_id == me.pk else link.from_user_id): link.status_for(me)
        for link in links
    }

    results = [
        {
            "pseudonym": p.pseudonym,
            "initial": p.pseudonym[:1].upper(),
            "photo_url": p.photo.url if p.photo else None,
            "profile_url": reverse("accounts:player_profile", args=[p.pseudonym]) + "?from=friends",
            "add_url": reverse("friends:send_request", args=[p.pseudonym]),
            "status": statuses.get(p.user_id, Friendship.NONE),
        }
        for p in profiles
    ]
    return JsonResponse({"results": results})


@login_required
@require_POST
def send_request(request, pseudonym):
    sender = request.user
    get_user_profile(sender)
    target = Profile.objects.select_related(
        "user").filter(pseudonym=pseudonym).first()

    if target is None:
        message, status_code = f"Le joueur « {pseudonym} » n'existe pas.", 404
    elif target.user_id == sender.pk:
        message, status_code = "Vous ne pouvez pas vous ajouter vous-même.", 400
    else:
        existing = Friendship.objects.filter(
            Q(from_user=sender, to_user=target.user) | Q(
                from_user=target.user, to_user=sender)
        ).first()

        if existing is None:
            try:
                with transaction.atomic():
                    Friendship.objects.create(
                        from_user=sender, to_user=target.user)
                outcome = "sent"
            except IntegrityError:
                existing = Friendship.objects.filter(
                    Q(from_user=sender, to_user=target.user) | Q(
                        from_user=target.user, to_user=sender)
                ).first()
                if existing is None:
                    outcome = "already_sent"
                elif existing.status == Friendship.ACCEPTED:
                    outcome = "already_friends"
                elif existing.from_user_id == sender.pk:
                    outcome = "already_sent"
                else:
                    existing.status = Friendship.ACCEPTED
                    existing.save(update_fields=["status"])
                    outcome = "accepted"
        elif existing.status == Friendship.ACCEPTED:
            outcome = "already_friends"
        elif existing.from_user_id == sender.pk:
            outcome = "already_sent"
        else:
            existing.status = Friendship.ACCEPTED
            existing.save(update_fields=["status"])
            outcome = "accepted"

        level, template, status = SEND_OUTCOMES[outcome]
        message = template.format(pseudonym=target.pseudonym)

        if is_ajax(request):
            return JsonResponse(
                {"success": True, "level": LEVEL_NAMES.get(
                    level, "info"), "status": status, "message": message}
            )
        messages.add_message(request, level, message)
        return redirect_back(request)

    if is_ajax(request):
        return JsonResponse(
            {"success": False, "level": "error", "message": message}, status=status_code
        )
    messages.error(request, message)
    return redirect_back(request)


def _pending_request_for(request, pk):
    return Friendship.objects.filter(pk=pk, to_user=request.user, status=Friendship.PENDING).select_related("from_user__profile").first()


@login_required
@require_POST
def accept_request(request, pk):
    friendship = _pending_request_for(request, pk)
    if friendship is None:
        return respond(request, messages.INFO, "Cette demande d'ami n'existe plus.", success=False)
    friendship.status = Friendship.ACCEPTED
    friendship.save(update_fields=["status"])
    return respond(
        request,
        messages.SUCCESS,
        f"Vous êtes maintenant ami avec {friendship.from_user.profile.pseudonym}.",
    )


@login_required
@require_POST
def decline_request(request, pk):
    friendship = _pending_request_for(request, pk)
    if friendship is None:
        return respond(request, messages.INFO, "Cette demande d'ami n'existe plus.", success=False)
    pseudonym = friendship.from_user.profile.pseudonym
    friendship.delete()
    return respond(request, messages.INFO, f"Vous avez refusé la demande de {pseudonym}.")


@login_required
@require_POST
def cancel_request(request, pk):
    friendship = (
        Friendship.objects.filter(
            pk=pk, from_user=request.user, status=Friendship.PENDING)
        .select_related("to_user__profile")
        .first()
    )
    if friendship is None:
        return respond(request, messages.INFO, "Cette demande d'ami n'existe plus.", success=False)
    pseudonym = friendship.to_user.profile.pseudonym
    friendship.delete()
    return respond(request, messages.INFO, f"Votre demande à {pseudonym} a été annulée.")


@login_required
@require_POST
def remove_friend(request, pk):
    friendship = (
        Friendship.objects.filter(
            Q(from_user=request.user) | Q(to_user=request.user),
            pk=pk,
            status=Friendship.ACCEPTED,
        )
        .select_related("from_user__profile", "to_user__profile")
        .first()
    )
    if friendship is None:
        return respond(request, messages.INFO, "Cette personne ne fait plus partie de vos amis.", success=False)
    other = (
        friendship.to_user
        if friendship.from_user_id == request.user.pk
        else friendship.from_user
    )
    pseudonym = other.profile.pseudonym
    friendship.delete()
    return respond(request, messages.INFO, f"{pseudonym} a été retiré de votre liste d'amis.")


@login_required
@require_POST
def invite_friend(request, pseudonym):
    """Enregistre l'invitation d'un ami à rejoindre la partie en cours."""
    from games.presence import get_identity, has_reservation
    from games.views import JEUX_MULTIJOUEUR

    me = request.user
    room_name = request.POST.get("room_name", "").strip()
    game_slug = request.POST.get("game_slug", "").strip()

    target = Profile.objects.select_related(
        "user").filter(pseudonym=pseudonym).first()
    if target is None:
        return JsonResponse({"ok": False, "error": "Joueur introuvable."}, status=404)

    est_ami = Friendship.objects.filter(
        Q(from_user=me, to_user=target.user) | Q(
            from_user=target.user, to_user=me),
        status=Friendship.ACCEPTED,
    ).exists()
    if not est_ami:
        return JsonResponse({"ok": False, "error": "Ce joueur n'est pas votre ami."}, status=403)

    if game_slug not in JEUX_MULTIJOUEUR or not room_name:
        return JsonResponse({"ok": False, "error": "Partie invalide."}, status=400)

    _, consumer = JEUX_MULTIJOUEUR[game_slug]
    identity = get_identity(me, request.session)
    if (
        consumer.ROOMS.get(room_name) is None
        and not has_reservation(identity, consumer.GAME_PREFIX, room_name)
    ):
        return JsonResponse({"ok": False, "error": "Cette partie n'existe pas."}, status=404)

    room = consumer.ROOMS.get(room_name)
    if room is not None and len(room["players"]) >= consumer.MAX_PLAYERS:
        return JsonResponse({"ok": False, "error": "La partie est déjà complète."}, status=409)

    GameInvitation.objects.update_or_create(
        from_user=me,
        to_user=target.user,
        room_name=room_name,
        defaults={
            "game_slug": game_slug,
            "status": GameInvitation.PENDING,
            "created_at": timezone.now(),
        },
    )
    return JsonResponse({"ok": True})


@login_required
def join_invitation(request, pk):
    """Lien « Rejoindre » de la notification : revérifie la partie puis y redirige."""
    from games.presence import MESSAGES, check_join, get_identity
    from games.views import JEUX_MULTIJOUEUR

    invitation = GameInvitation.objects.filter(
        pk=pk, to_user=request.user, status=GameInvitation.PENDING
    ).first()
    if invitation is None:
        messages.error(request, "Cette invitation n'est plus valide.")
        return redirect("home")

    if invitation.is_expired() or invitation.game_slug not in JEUX_MULTIJOUEUR:
        messages.error(request, "Cette invitation a expiré.")
        return redirect("home")

    url_name, consumer = JEUX_MULTIJOUEUR[invitation.game_slug]
    room = consumer.ROOMS.get(invitation.room_name)
    identity = get_identity(request.user, request.session, create=True)

    if room is None:
        messages.error(request, "Cette partie n'existe plus.")
        return redirect("home")

    refus = check_join(
        identity, True, consumer.GAME_PREFIX,
        invitation.room_name, room, consumer.MAX_PLAYERS,
    )
    if refus:
        messages.error(request, MESSAGES[refus])
        return redirect("home")

    invitation.status = GameInvitation.ACCEPTED
    invitation.save(update_fields=["status"])
    return redirect(url_name, room_name=invitation.room_name)
