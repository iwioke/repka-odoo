from . import models


def post_init_hook(env):
    env.ref("base.user_admin").write({"is_redirect_home": True})
