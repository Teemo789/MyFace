# MyFace

Système d'authentification Python combinant mot de passe et reconnaissance faciale avec contrôle des poses (face, gauche, droite, haut, bas) à l'aide d'OpenCV, MediaPipe, face_recognition et bcrypt.

## Structure
```
project/
 ├─ register.py          # Inscription + capture des 5 poses
 ├─ login.py             # Connexion + vérification faciale
 ├─ db.json              # Stockage JSON des utilisateurs
 └─ utils/
     ├─ face_capture.py  # Capture webcam, détection de pose, encodage visage
     ├─ hashing.py       # Hachage/validation bcrypt
     └─ database.py      # Lecture/écriture JSON
```
## Utilisation

2. Inscription :
   ```bash
   cd project
   python register.py
   ```
3. Connexion :
   ```bash
   cd project
   python login.py
   ```

La base `db.json` est mise à jour automatiquement après chaque inscription.

### Conseils d'utilisation
- Tous les champs demandés lors de l'inscription sont obligatoires.
- Si la caméra n'est pas accessible, les scripts interrompent l'exécution avec un message explicite.
- Appuyez sur `q` pendant la capture pour annuler la tentative en cours.
