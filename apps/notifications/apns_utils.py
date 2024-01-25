from pyapns import configure, provision, notify

configure({'HOST': 'gateway.sandbox.push.apple.com'})
provision('путь_к_вашему_файлу_ключа.pem', 'пароль_ключа', 'bundle_id')