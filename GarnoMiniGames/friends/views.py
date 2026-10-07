from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST

from accounts.models import Profile
from accounts.views import get_user_profile, is_ajax

from .models import Friendship

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


@login_required
def friends_list(request):
    me = request.user
    get_user_profile(me)

    friendships = Friendship.objects.filter(
        Q(from_user=me) | Q(to_user=me),
        status=Friendship.ACCEPTED,
    ).select_related("from_user__profile", "to_user__profile")

    friends = []
    for friendship in friendships:
        other = friendship.to_user if friendship.from_user_id == me.pk else friendship.from_user
        friends.append({"friendship": friendship, "profile": other.profile})
    friends.sort(key=lambda item: item["profile"].pseudonym.lower())

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
            "profile_url": reverse("accounts:player_profile", args=[p.pseudonym]),
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
            Friendship.objects.create(from_user=sender, to_user=target.user)
            outcome = "sent"
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
            return JsonResponse({"success": True, "status": status, "message": message})
        messages.add_message(request, level, message)
        return redirect_back(request)

    if is_ajax(request):
        return JsonResponse({"success": False, "message": message}, status=status_code)
    messages.error(request, message)
    return redirect_back(request)


def _pending_request_for(request, pk):
    return Friendship.objects.filter(pk=pk, to_user=request.user, status=Friendship.PENDING).select_related("from_user__profile").first()


@login_required
@require_POST
def accept_request(request, pk):
    friendship = _pending_request_for(request, pk)
    if friendship is None:
        messages.info(request, "Cette demande d'ami n'existe plus.")
    else:
        friendship.status = Friendship.ACCEPTED
        friendship.save(update_fields=["status"])
        messages.success(
            request,
            f"Vous êtes maintenant ami avec {friendship.from_user.profile.pseudonym}.",
        )
    return redirect_back(request)


@login_required
@require_POST
def decline_request(request, pk):
    friendship = _pending_request_for(request, pk)
    if friendship is None:
        messages.info(request, "Cette demande d'ami n'existe plus.")
    else:
        pseudonym = friendship.from_user.profile.pseudonym
        friendship.delete()
        messages.info(request, f"Vous avez refusé la demande de {pseudonym}.")
    return redirect_back(request)


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
        messages.info(request, "Cette demande d'ami n'existe plus.")
    else:
        pseudonym = friendship.to_user.profile.pseudonym
        friendship.delete()
        messages.info(request, f"Votre demande à {pseudonym} a été annulée.")
    return redirect_back(request)


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
        messages.info(
            request, "Cette personne ne fait plus partie de vos amis.")
    else:
        other = (
            friendship.to_user
            if friendship.from_user_id == request.user.pk
            else friendship.from_user
        )
        pseudonym = other.profile.pseudonym
        friendship.delete()
        messages.info(
            request, f"{pseudonym} a été retiré de votre liste d'amis.")
    return redirect_back(request)
