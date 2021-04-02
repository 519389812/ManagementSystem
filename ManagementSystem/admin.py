def return_get_queryset_by_team_regex(request, qs, field_name):
    if not request.user.is_superuser:
        try:
            team_id = request.user.team.id
            qs = eval("qs.filter(%s__related_parent__iregex=r'\D%s\D')" % (field_name, str(team_id)))
        except:
            pass
    return qs


def return_get_queryset_by_team(request, qs, field_name):
    if not request.user.is_superuser:
        try:
            qs = eval("qs.filter(%s__in=[request.user.team])" % field_name)
        except:
            pass
    return qs
