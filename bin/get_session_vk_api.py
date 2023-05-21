from vk_api import VkApi, VkTools


def get_session_vk_api(session, vkapp=False, vktools=False):
    try:
        vk_session = VkApi(token=session['tokens'][session['name_work_token']])
        if vkapp:
            session['vk_app'] = vk_session.get_api()
        if vktools:
            session['tools'] = VkTools(vk_session)
        return session
    except Exception as exc:
        print(exc)
    return session
