# migrate_db_prefix.py
# SCRIPT DE RÉPARATION D'URGENCE. NE PAS MODIFIER.

import os
from replit import db
import time

print("--- [OUTIL DE RÉPARATION] Démarrage ---")
time.sleep(1)

# Ancien préfixe où se trouvent VOS DONNÉES ACTUELLES
OLD_PREFIX = "user:"

# Nouveau préfixe que le bot recherche maintenant
# Il va lire le Secret "DB_PREFIX" que vous avez défini sur "prod"
DB_ENV_PREFIX = os.getenv("DB_PREFIX")
if not DB_ENV_PREFIX:
    print(
        "\n\n❌ ERREUR FATALE: Le Secret 'DB_PREFIX' n'est pas défini. Allez dans l'onglet 'Secrets' (cadenas) et créez une clé 'DB_PREFIX' avec la valeur 'prod'."
    )
    exit()

NEW_USER_PREFIX = f"{DB_ENV_PREFIX}_user:"

print(
    f"Vos données vont être renommées de '{OLD_PREFIX}...' à '{NEW_USER_PREFIX}...'."
)
print("-" * 40)
time.sleep(3)

keys_to_migrate = [key for key in db.keys() if key.startswith(OLD_PREFIX)]

if not keys_to_migrate:
    print(
        "✅ BONNE NOUVELLE: Aucune clé à migrer n'a été trouvée. Vos données sont probablement déjà au bon format."
    )
    print("Passez directement à l'étape 2 (lancer rebuild_cache.py).")
    exit()

print(f"🔍 {len(keys_to_migrate)} utilisateurs trouvés. Début du renommage...")
time.sleep(2)

migrated_count = 0
error_count = 0

for old_key in keys_to_migrate:
    try:
        new_key = old_key.replace(OLD_PREFIX, NEW_USER_PREFIX)

        # On vérifie que la nouvelle clé n'existe pas déjà pour éviter d'écraser des données
        if new_key in db:
            print(f"  ⚠️  Ignoré '{old_key}' car '{new_key}' existe déjà.")
            continue

        # Copie la donnée vers la nouvelle clé
        db[new_key] = db[old_key]
        # Supprime l'ancienne clé
        del db[old_key]

        migrated_count += 1
    except Exception as e:
        print(f"  ❌ ERREUR en migrant la clé '{old_key}': {e}")
        error_count += 1

print("-" * 40)
if error_count > 0:
    print(f"⚠️ Migration terminée avec {error_count} erreurs.")
else:
    print(
        f"✅ Migration terminée avec succès. {migrated_count} utilisateurs ont été mis à jour."
    )

print("\nLa base de données est réparée.")
print("Passez à l'étape suivante.")
