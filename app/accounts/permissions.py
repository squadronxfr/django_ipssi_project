"""
Définitions des permissions et groupes pour l'application accounts.
"""

# Noms des groupes
ADMIN_GROUP = "admin_group"
RECRUITER_GROUP = "recruteur_group"
CANDIDATE_GROUP = "candidat_group"

CAN_MANAGE_USERS = "can_manage_users"
CAN_MANAGE_RECRUITMENT = "can_manage_recruitment"
CAN_APPLY_JOBS = "can_apply_jobs"

# Permissions de modèle UserProfile de Django (add/change/delete/view)
ADD_USERPROFILE = "add_userprofile"
CHANGE_USERPROFILE = "change_userprofile"
DELETE_USERPROFILE = "delete_userprofile"
VIEW_USERPROFILE = "view_userprofile"

# Mapping des permissions par groupe
GROUP_PERMISSIONS = {
    ADMIN_GROUP: {
        # toutes les permissions sur UserProfile + permissions custom
        ADD_USERPROFILE,
        CHANGE_USERPROFILE,
        DELETE_USERPROFILE,
        VIEW_USERPROFILE,
        CAN_MANAGE_USERS,
        CAN_MANAGE_RECRUITMENT,
        CAN_APPLY_JOBS,
    },
    RECRUITER_GROUP: {
        VIEW_USERPROFILE,
        CHANGE_USERPROFILE,
        CAN_MANAGE_RECRUITMENT,
    },
    CANDIDATE_GROUP: {
        VIEW_USERPROFILE,
        CAN_APPLY_JOBS,
    },
}
