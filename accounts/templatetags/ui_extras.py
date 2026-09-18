from django import template
from django.utils.html import format_html

register = template.Library()

# Same palette devboard-design's mock users use (indigo/emerald/amber/pink/violet).
AVATAR_COLORS = ['#6366F1', '#10B981', '#F59E0B', '#EC4899', '#8B5CF6']


def _initials(name: str) -> str:
    parts = [p for p in name.replace('.', ' ').replace('_', ' ').split() if p]
    if not parts:
        return '?'
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


@register.simple_tag
def avatar(name, size=''):
    """Initials-on-a-color circle, ported from AppShell.tsx's Avatar(). Color is
    picked deterministically from the name so the same person always gets the
    same color across pages, without storing one anywhere."""
    name = name or '?'
    color = AVATAR_COLORS[sum(ord(c) for c in name) % len(AVATAR_COLORS)]
    size_class = 'avatar-circle-sm' if size == 'sm' else ''
    return format_html(
        '<span class="avatar-circle {}" style="background-color: {}" title="{}">{}</span>',
        size_class, color, name, _initials(name),
    )


@register.simple_tag
def team_avatar(name):
    """Rounded-square single-letter mark for a team, ported from AppShell.tsx's
    team-switcher button (currentTeam.avatarColor / currentTeam.name[0])."""
    name = name or '?'
    color = AVATAR_COLORS[sum(ord(c) for c in name) % len(AVATAR_COLORS)]
    return format_html(
        '<span class="avatar-square" style="background-color: {}">{}</span>',
        color, name[0].upper(),
    )
