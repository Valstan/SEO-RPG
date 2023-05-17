from vk_api import VkApi, VkTools


def get_session_vk_api(session):
    for i in range(3):
        if session['token']:
            try:
                vk_session = VkApi(token=session['token'])
                session['vk_app'] = vk_session.get_api()
                session['tools'] = VkTools(vk_session)
                return session
            except Exception as exc:
                print(exc)
        else:
            try:
                vk_session = VkApi(session['login'], session['password'])
                vk_session.auth()
                session['vk_app'] = vk_session.get_api()
                session['tools'] = VkTools(vk_session)
                return session
            except Exception as exc:
                print(exc)
    return session
