def get_attach(msg):
    if 'attachments' in msg:
        attach = ''
        for sample in msg['attachments']:
            type_attach = sample['type']
            if type_attach == 'link':
                return sample[type_attach]['url']
            elif type_attach == 'photos_list':
                attach += ''.join(map(str, (type_attach, sample[type_attach], ',')))
            else:
                attach += ''.join(map(str, (type_attach, sample[type_attach]['owner_id'],
                                            '_', sample[type_attach]['id'], ',')))
        return attach[:-1]
    else:
        return ''
