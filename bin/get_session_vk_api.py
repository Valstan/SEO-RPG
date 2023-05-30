from vk_api import VkApi, VkTools


# from requests import Session, get
# import random
# from bs4 import BeautifulSoup


# def get_free_proxies():
#     url = "https://free-proxy-list.net/"
#     # получаем ответ HTTP и создаем объект soup
#     soup = BeautifulSoup(get(url).content, "html.parser")
#     table_proxy = soup.find("table").find_all("tr")[1:]
#     proxies = []
#     for row in table_proxy:
#
#         tds = row.find_all("td")
#
#         if "elite proxy" in tds[4] and "yes" in tds[6]:
#             try:
#                 ip = tds[0].text.strip()
#                 port = tds[1].text.strip()
#                 host = f"{ip}:{port}"
#                 proxies.append(host)
#             except IndexError:
#                 continue
#
#     return proxies
#
#
# def get_session(proxies):
#     # создать HTTP‑сеанс
#     session = Session()
#     # выбираем один случайный прокси
#     proxy = random.choice(proxies)
#     session.proxies = {"http": proxy, "https": proxy}
#     return session


# def get_session_vk_api(msession, vkapp=False, vktools=False):
#     free_proxies = get_free_proxies()
#     for i in range(200):
#         proxy = random.choice(free_proxies)
#         print("Пробую другую проксю...")
#         session = Session()
#         session.proxies = {"http": proxy, "https": proxy}
#
#         try:
#             vk_session = VkApi(token=msession['tokens'][msession['name_work_token']], session=session)
#             if vkapp:
#                 msession['vk_app'] = vk_session.get_api()
#             if vktools:
#                 msession['tools'] = VkTools(vk_session)
#             return msession
#         except Exception as exc:
#             print(exc)
#             time.sleep(2)

def get_session_vk_api(session, vkapp=False, vktools=False):
    vk_session = VkApi(token=session['tokens'][session['name_work_token']])
    if vkapp:
        session['vk_app'] = vk_session.get_api()
    if vktools:
        session['tools'] = VkTools(vk_session)
    return session
