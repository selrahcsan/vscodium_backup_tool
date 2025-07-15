import os
import shutil
import subprocess
import gettext
from datetime import datetime

LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locales')
LANGUAGE = os.getenv("LANG", "pt_BR").split('.')[0] 

try:
    translation = gettext.translation('messages', LOCALE_DIR, languages=[LANGUAGE])
    translation.install()
    _ = translation.gettext
except FileNotFoundError:
    gettext.install('messages')
    _ = gettext.gettext

HOME = os.path.expanduser("~")
CONFIG_DIR = os.path.join(HOME, ".config", "VSCodium", "User")
BACKUP_BASE_DIR = os.path.join(HOME, "vscodium-backups")

def backup():
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(BACKUP_BASE_DIR, f"backup_{date_str}")
    os.makedirs(backup_dir, exist_ok=True)

    print(_("📁 Copying settings..."))
    shutil.copytree(CONFIG_DIR, os.path.join(backup_dir, "User"))

    extensions_file = os.path.join(backup_dir, "extensions.txt")
    print(_("🧩 Exporting extension list..."))
    with open(extensions_file, "w") as f:
        subprocess.run(["codium", "--list-extensions"], stdout=f)

    print(_("✅ Backup completed at: {}").format(backup_dir))

def restore():
    backups = sorted(os.listdir(BACKUP_BASE_DIR))
    if not backups:
        print(_("❌ No backups found."))
        return

    print(_("\n📦 Available backups:"))
    for i, b in enumerate(backups):
        print(f"[{i}] {b}")

    choice = input(_("Choose the number of the backup to restore: "))
    try:
        index = int(choice)
        selected_backup = os.path.join(BACKUP_BASE_DIR, backups[index])
    except (ValueError, IndexError):
        print(_("❌ Invalid choice."))
        return

    print(_("🔄 Restoring configuration..."))
    if os.path.exists(CONFIG_DIR):
        shutil.rmtree(CONFIG_DIR)
    shutil.copytree(os.path.join(selected_backup, "User"), CONFIG_DIR)

    extensions_file = os.path.join(selected_backup, "extensions.txt")
    if os.path.exists(extensions_file):
        print(_("📥 Reinstalling extensions..."))
        with open(extensions_file) as f:
            for ext in f:
                subprocess.run(["codium", "--install-extension", ext.strip()])
    else:
        print(_("⚠️ No extension list found."))

    print(_("✅ Restore completed!"))

def menu():
    while True:
        print("\n" + _("=== VSCodium Backup Tool ==="))
        print(_("1. Create backup"))
        print(_("2. Restore backup"))
        print(_("3. Exit"))

        choice = input(_("Choose an option: "))
        if choice == "1":
            backup()
        elif choice == "2":
            restore()
        elif choice == "3":
            print(_("👋 Exiting..."))
            break
        else:
            print(_("❌ Invalid option!"))

if __name__ == "__main__":
    os.makedirs(BACKUP_BASE_DIR, exist_ok=True)
    menu()