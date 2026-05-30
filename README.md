# 🔐 LAB 17 — OWASP UnCrackable Android Level 3

![Android](https://img.shields.io/badge/Android-Reverse%20Engineering-3DDC84?style=for-the-badge&logo=android&logoColor=white)
![Ghidra](https://img.shields.io/badge/Ghidra-Native%20Analysis-red?style=for-the-badge)
![Jadx](https://img.shields.io/badge/Jadx-Java%20Decompilation-blue?style=for-the-badge)
![Apktool](https://img.shields.io/badge/Apktool-Smali%20Patch-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Success-brightgreen?style=for-the-badge)

## 📌 Présentation du laboratoire

Ce laboratoire porte sur l’analyse et le contournement des protections de l’application **OWASP UnCrackable Android Level 3**.

L’objectif est de comprendre comment une application Android peut combiner du code Java, du code Smali et une librairie native `.so` afin de protéger une vérification de mot de passe.

Le travail réalisé couvre :

- l’analyse statique du code Java avec **Jadx-GUI** ;
- la décompilation et modification Smali avec **apktool** ;
- le contournement des protections root / debug / tampering ;
- l’analyse native de `libfoo.so` avec **Ghidra** ;
- le patch d’une fonction anti-Frida / anti-Xposed ;
- l’extraction du secret grâce à une logique XOR byte par byte.

---

## 🎯 Objectifs pédagogiques

À la fin de ce laboratoire, les compétences suivantes ont été mises en pratique :

- Décompiler une APK Android.
- Identifier les protections Java et natives.
- Modifier du code Smali.
- Recompiler, signer et réinstaller une APK patchée.
- Analyser une librairie native `.so`.
- Comprendre le fonctionnement d’une fonction JNI.
- Identifier une vérification XOR.
- Retrouver un secret à partir d’octets chiffrés et d’une clé.

---

## 🧰 Outils utilisés

| Outil | Rôle |
|---|---|
| **Android Studio / Emulator** | Exécution et test de l’application |
| **ADB** | Installation, désinstallation et interaction avec l’émulateur |
| **Jadx-GUI** | Décompilation Java de l’APK |
| **apktool** | Décompilation et reconstruction de l’APK |
| **VS Code** | Modification du fichier Smali |
| **Ghidra** | Analyse et patch de la librairie native |
| **Python** | Calcul du secret par XOR |

---

## 📁 Structure du dépôt

```text
LAB17_uncrackable3/
├── screenshots/
│   ├── MainActivity_verifyLibs.png
│   ├── MainActivity_rooting-or-tampering-detected.png
│   ├── MainActivity_System-loadLibrary.png
│   ├── MainActivity-smali_vscode.png
│   ├── code_modifcation_MainActivity-smali_vscode.png
│   ├── apktool_uncrackableL3.png
│   ├── apk_rebuild.png
│   ├── apk_sign.png
│   ├── libfoo-so_import_ghidra.png
│   ├── libfoo-so_analysis_ghidra.png
│   ├── proc-self-maps.png
│   ├── frida.png
│   ├── xposed.png
│   ├── 001037c0_patch_instruction.png
│   ├── instruction_patched.png
│   ├── symbol-tree_codecheck_ghidra.png
│   ├── decompiled_function.png
│   ├── function_FUN_001012c0.png
│   ├── xor_vscode.png
│   └── secret_found.png
├── test.py
├── .gitignore
└── README.md
```
> Les fichiers générés comme les APK, les librairies `.so`, les dossiers apktool et les projets Ghidra ne sont pas versionnés afin de garder le dépôt propre.

---

# 🧩 Étape 1 — Installation et test de l’APK original

L’APK original a d’abord été installée sur l’émulateur avec `adb`.

```bash
adb install -r UnCrackable-Level3.apk
```

L’application s’ouvre avec un champ permettant d’entrer une chaîne secrète.

<p align="center">
  <img width="1280" height="2856" alt="enter_secretstring" src="https://github.com/user-attachments/assets/3871f3ec-293f-4cf7-a20b-d6c7a2e71e68">
</p>

---

# 🔎 Étape 2 — Analyse statique avec Jadx-GUI

L’APK est ouverte dans **Jadx-GUI** afin d’observer le code Java décompilé.

Dans `MainActivity`, plusieurs éléments importants apparaissent.

## Vérification d’intégrité

La méthode `verifyLibs()` vérifie les CRC des librairies natives et du fichier `classes.dex`.

<p align="center">
  <img width="1365" height="724" alt="MainActivity_verifyLibs" src="https://github.com/user-attachments/assets/1e99367d-438b-4e56-9566-6b921db9cb86" />

</p>

Cette méthode permet de détecter si l’APK ou ses librairies ont été modifiées.

---

## Détection root / debug / tampering

Dans `onCreate()`, l’application vérifie plusieurs conditions :

- détection root ;
- détection debug ;
- vérification d’intégrité ;
- variable `tampered`.

Si une anomalie est détectée, un message d’erreur est affiché.

<p align="center">
  <img width="1366" height="726" alt="MainActivity_rooting-or-tampering-detected" src="https://github.com/user-attachments/assets/21884eeb-4191-49d9-8c4d-2af685e6ab12" />

</p>

---

## Chargement de la librairie native

La ligne suivante montre que la librairie native `libfoo.so` est chargée :

```java
System.loadLibrary("foo");
```

<p align="center">
  <img width="1366" height="727" alt="MainActivity_System-loadLibrary" src="https://github.com/user-attachments/assets/80bbf2f9-228f-4883-85b3-5f842db61eb3" />

</p>

Cela indique que la vérification réelle du secret est effectuée côté natif.

---

# 🛠️ Étape 3 — Décompilation avec apktool

L’APK est ensuite décompilée avec `apktool`.

```bash
java -jar apktool.jar d -f UnCrackable-Level3.apk -o uncrackable3
```

<p align="center">
  <img width="1208" height="236" alt="apktool_uncrackableL3" src="https://github.com/user-attachments/assets/1f267b78-34c9-4e60-b63c-605439b872ba" />

</p>

Le dossier obtenu contient notamment :

```text
uncrackable3/
├── smali/
├── lib/
├── res/
├── AndroidManifest.xml
└── apktool.yml
```

Le fichier Smali principal se trouve dans :

```text
uncrackable3/smali/sg/vantagepoint/uncrackable3/MainActivity.smali
```

---

# ✏️ Étape 4 — Patch Smali

Le fichier `MainActivity.smali` est ouvert dans VS Code.

<p align="center">
  <img width="1352" height="731" alt="MainActivity-smali_vscode" src="https://github.com/user-attachments/assets/e2dd0b70-158c-4b65-978f-3c737a29f6cb" />

</p>

Le bloc responsable de l’affichage du message suivant est identifié :

```text
Rooting or tampering detected.
```

<p align="center">
  <img width="977" height="581" alt="find_Rooting-or-tampering-detected_MainActivity_vscode" src="https://github.com/user-attachments/assets/fc458370-9b84-479e-b123-26337823ae13" />

</p>

Le code original appelle la méthode `showDialog()` lorsque root, debug ou tampering est détecté.

Le patch consiste à remplacer l’appel au dialogue par un saut direct vers la suite normale du programme :

```smali
:cond_0
goto :cond_1
```

<p align="center">
 ![Uploading code_modifcation_MainActivity-smali_vscode.png…]()

</p>

Ce patch permet à l’application de continuer son exécution sans afficher le message d’erreur.

---

# 📦 Étape 5 — Reconstruction, signature et installation

Après modification du Smali, l’APK est reconstruite.

```bash
java -jar apktool.jar b uncrackable3 -o UnCrackable-Level3-patched.apk
```

<p align="center">
  <img width="1208" height="140" alt="apk_rebuild" src="https://github.com/user-attachments/assets/9b5fd12f-9636-4d8e-b386-5b5b7aafaf0a" />

</p>

L’APK est ensuite signée avec `apksigner`.

```bash
apksigner sign --ks "%USERPROFILE%\.android\debug.keystore" UnCrackable-Level3-patched.apk
```

<p align="center">
  <img width="1203" height="198" alt="apk_sign" src="https://github.com/user-attachments/assets/732e9259-f9e2-4451-88ce-5ff737ca8460" />

</p>

La signature est vérifiée :

```bash
apksigner verify --verbose UnCrackable-Level3-patched.apk
```

<p align="center">
  <img width="1204" height="245" alt="apk_sign_verify" src="https://github.com/user-attachments/assets/3c6499b6-2a24-4aa7-8f4f-836d5b24e957" />

</p>

Puis l’application patchée est installée sur l’émulateur.

```bash
adb uninstall owasp.mstg.uncrackable3
adb install -r UnCrackable-Level3-patched.apk
```

<p align="center">
  <img width="1156" height="130" alt="patched_apk_reinstall" src="https://github.com/user-attachments/assets/ec3ca593-81d5-41ef-a7e6-4e54f1fe1899" />

</p>

---

# 🧬 Étape 6 — Analyse native avec Ghidra

Comme l’émulateur utilise l’architecture `x86_64`, la librairie analysée est :

```text
uncrackable3/lib/x86_64/libfoo.so
```

La librairie est importée dans Ghidra.

<p align="center">
  <img width="1363" height="722" alt="libfoo-so_import_ghidra" src="https://github.com/user-attachments/assets/be7f8740-1ede-444b-a115-25ee769fe290" />

</p>

Après analyse automatique, Ghidra permet d’explorer les fonctions et les chaînes présentes dans la librairie.

<p align="center">
  

</p>

---

# 🛡️ Étape 7 — Détection anti-Frida / anti-Xposed

Une recherche de chaînes révèle la présence de plusieurs indicateurs de protection :

```text
/proc/self/maps
frida
xposed
```

<p align="center">
  <img width="905" height="675" alt="string_search_proc-self-maps" src="https://github.com/user-attachments/assets/4065086b-f6cd-4890-b3a7-b29ab4366373" />

</p>

<p align="center">
 <img width="911" height="681" alt="string_search_frida" src="https://github.com/user-attachments/assets/91aa2828-5a4c-43e8-8ef5-9b20c8616903" />

</p>

<p align="center">
  <img width="907" height="680" alt="string_search_xposed" src="https://github.com/user-attachments/assets/cd1df204-a4a8-48e3-bf90-1ad1f0d5bf85" />

</p>

Les références croisées montrent que ces chaînes sont utilisées dans la fonction :

```text
FUN_001037c0
```

Cette fonction ouvre `/proc/self/maps`, recherche les chaînes `frida` et `xposed`, puis déclenche `goodbye()` si une anomalie est détectée.

<p align="center">
  <img width="1366" height="725" alt="proc-self-maps_1streference-function" src="https://github.com/user-attachments/assets/ea26598c-1d92-49c6-a27c-127a28431173" />

</p>

---

# 🧨 Étape 8 — Patch de la fonction native

La fonction `FUN_001037c0` est patchée directement au début.

Instruction originale :

```asm
PUSH RBP
```

Instruction patchée :

```asm
RET
```

<p align="center">
  <img width="587" height="471" alt="001037c0_patch_instruction" src="https://github.com/user-attachments/assets/7e685b4d-6522-420b-af79-5f5da1df885a" />

</p>

Après patch :

<p align="center">
  <img width="968" height="321" alt="instruction_patched" src="https://github.com/user-attachments/assets/24fa7a67-8a92-482c-831f-9f5cc587cff4" />

</p>

Ce patch force la fonction à retourner immédiatement, ce qui contourne :

- la lecture de `/proc/self/maps` ;
- la détection Frida ;
- la détection Xposed ;
- l’appel à `goodbye()`.

---

# 💾 Étape 9 — Export de la librairie patchée

Après modification, la librairie est exportée depuis Ghidra au format :

```text
Original File
```

<p align="center">
  <img width="1080" height="692" alt="saving_patched-file_original-format" src="https://github.com/user-attachments/assets/28402d70-24d8-441f-9853-bf2d388c4d55" />

</p>

La librairie patchée est ensuite replacée dans :

```text
uncrackable3/lib/x86_64/libfoo.so
```

<p align="center">
  <img width="546" height="218" alt="moving_and_renaming_libfoo-so" src="https://github.com/user-attachments/assets/c66834c6-b1e1-4846-81f7-854db7322116" />

</p>

L’APK est reconstruite, signée, puis réinstallée.

<p align="center">
  <img width="984" height="138" alt="rebuilding_patched_apk_after_ghidra" src="https://github.com/user-attachments/assets/4e83f915-23ff-44bc-a390-8da408c1c920" />

</p>

<p align="center">
  <img src="screenshots/signing_patched_apk_after_ghidra.png" width="850">
</p>

<p align="center">
  <img width="1349" height="198" alt="signing_patched_apk_after_ghidra" src="https://github.com/user-attachments/assets/3502eac2-db65-473c-a40e-42c969eabf72" />

</p>

---

# 🔐 Étape 10 — Analyse de la fonction de vérification du secret

Dans Jadx, la classe `CodeCheck` montre que la méthode Java appelle une fonction native :

```java
private native boolean bar(byte[] bArr);

public boolean check_code(String str) {
    return bar(str.getBytes());
}
```

<p align="center">
  <img width="1334" height="477" alt="jdx_codecheck" src="https://github.com/user-attachments/assets/70c2733f-b4c0-434e-bfa6-c051038aa4ed" />

</p>

Dans Ghidra, la fonction correspondante est :

```text
Java_sg_vantagepoint_uncrackable3_CodeCheck_bar
```

<p align="center">
  <img width="1201" height="323" alt="symbol-tree_codecheck_ghidra" src="https://github.com/user-attachments/assets/b9bb2626-c5e0-466e-b214-d8cbfa5ab715" />

</p>

La fonction vérifie d’abord que l’entrée utilisateur possède une longueur de `0x18`.

```text
0x18 = 24
```

Le secret doit donc contenir **24 caractères**.

---

# 🧮 Étape 11 — Compréhension du XOR

La fonction native compare chaque octet de l’entrée utilisateur avec le résultat d’un XOR.

La logique peut être résumée ainsi :

```text
input[i] == DAT_00107040[i] XOR local_48[i]
```

Donc, pour retrouver le secret :

```text
secret[i] = DAT_00107040[i] XOR local_48[i]
```

<p align="center">
  <img width="744" height="636" alt="decompiled_function" src="https://github.com/user-attachments/assets/74ab0af7-09c6-454e-9c70-d557efc4304b" />

</p>

La fonction `FUN_001012c0` génère la clé utilisée dans `local_48`.

<p align="center">
  <img width="620" height="371" alt="function_FUN_001012c0" src="https://github.com/user-attachments/assets/b56410c9-0769-4dfb-8296-a31f9172f989" />

</p>

Les trois constantes utilisées représentent 24 octets au total :

```text
3 blocs × 8 octets = 24 octets
```

Comme l’architecture est `x86_64`, les valeurs sont stockées en little-endian.

La clé obtenue est :

```text
1d 08 11 13 0f 17 49 15
0d 00 03 19 5a 1d 13 15
08 0e 5a 00 17 08 13 14
```

---

# 🐍 Étape 12 — Script Python de calcul du secret

Le script Python applique le XOR entre les octets de `DAT_00107040` et la clé générée dans `local_48`.

```python
dat = bytes.fromhex(
    "70 69 7a 7a 61 70 69 7a "
    "7a 61 70 69 7a 7a 61 70 "
    "69 7a 7a 61 70 69 7a 7a"
)

key = bytes.fromhex(
    "1d 08 11 13 0f 17 49 15 "
    "0d 00 03 19 5a 1d 13 15 "
    "08 0e 5a 00 17 08 13 14"
)

secret = bytes([d ^ k for d, k in zip(dat, key)])
print(secret.decode())
```

<p align="center">
  <img width="1016" height="680" alt="xor_vscode" src="https://github.com/user-attachments/assets/bae15f50-a757-40ae-b421-c77d2ed60bb7" />

</p>

Le résultat obtenu est :

```text
making owasp great again
```

---

# ✅ Résultat final

Le secret est saisi dans l’application :

```text
making owasp great again
```

L’application confirme que le secret est correct.

<p align="center">
  <img width="459" height="559" alt="secret_found" src="https://github.com/user-attachments/assets/e4f1dcb6-799c-4566-bb2b-a94d023e95e9" />

</p>

---

# 🧠 Résumé technique

| Étape | Résultat |
|---|---|
| Analyse Java | Identification de `verifyLibs()`, `showDialog()` et `System.loadLibrary("foo")` |
| Patch Smali | Contournement du message root / tampering |
| Rebuild APK | APK reconstruite avec apktool |
| Signature | APK signée avec apksigner |
| Analyse native | Identification de `FUN_001037c0` |
| Patch natif | Remplacement de la première instruction par `RET` |
| Analyse du secret | Identification de `CodeCheck_bar` |
| XOR | Extraction du secret final |
| Validation | Message `Success! This is the correct secret.` |

---

# 📌 Commandes principales utilisées

```bash
adb devices
adb shell getprop ro.product.cpu.abi
adb install -r UnCrackable-Level3.apk
```

```bash
java -jar apktool.jar d -f UnCrackable-Level3.apk -o uncrackable3
```

```bash
java -jar apktool.jar b uncrackable3 -o UnCrackable-Level3-patched.apk
```

```bash
apksigner sign --ks "%USERPROFILE%\.android\debug.keystore" UnCrackable-Level3-patched.apk
```

```bash
adb uninstall owasp.mstg.uncrackable3
adb install -r UnCrackable-Level3-patched.apk
```

---

# ⚠️ Remarque

Ce travail a été réalisé dans un cadre académique, sur une application volontairement vulnérable fournie par OWASP pour l’apprentissage de la sécurité mobile.

L’objectif est uniquement pédagogique :

- comprendre les protections Android ;
- apprendre l’analyse statique et native ;
- manipuler les outils de reverse engineering ;
- documenter une démarche de sécurité offensive encadrée.

---

# 🏁 Conclusion

Ce laboratoire montre comment une application Android peut utiliser plusieurs couches de protection : Java, Smali, vérification d’intégrité, détection d’environnement suspect et logique native.

Grâce à l’analyse avec Jadx, apktool et Ghidra, il a été possible de :

- contourner les protections Java ;
- patcher une fonction native ;
- comprendre la logique XOR ;
- retrouver le secret final ;
- valider le résultat dans l’application.

Le secret final obtenu est :

```text
making owasp great again
```
