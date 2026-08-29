from . import models


def post_init_hook(env):
    env.ref("base.user_admin").write({
        "is_redirect_home": True,
        "groups_id": [(4, env.ref("repka_logistics_core.group_42").id)],
    })
