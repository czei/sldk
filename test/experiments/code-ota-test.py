from src.ota.ota_updater import OTAUpdater

token='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'
updater = OTAUpdater('https://github.com/Czeiszperger/themeparkwaits.release', main_dir="src", headers={'Authorization': 'token {}'.format(token)})
print (f"Release version is {updater.get_version("src")}")