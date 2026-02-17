"""
Script pour lancer l'application.
"""
import subprocess
import sys
import os

def main():
    """Fonction principale."""
    print("=" * 60)
    print("🚀 OPSGAIN PLATFORM/PORT SEC INTELLIGENT")
    print("=" * 60)
    
    # Vérification de l'environnement
    print("\n🔍 Vérification de l'environnement...")
    
    # Vérifier Python
    try:
        import sys
        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor >= 9:
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            print(f"❌ Python {python_version.major}.{python_version.minor} - Version 3.9+ requise")
            return
    except:
        print("❌ Python non détecté")
        return
    
    # Vérifier les dossiers
    required_dirs = ['.streamlit', 'assets', 'data/logs/access', 'src']
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Dossier: {dir_path}")
        else:
            print(f"⚠️  Dossier manquant: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            print(f"   Créé: {dir_path}")
    
    # Vérifier les fichiers requis
    required_files = ['app.py', 'requirements.txt', '.streamlit/config.toml']
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ Fichier: {file_path}")
        else:
            print(f"❌ Fichier manquant: {file_path}")
            return
    
    # Installation des dépendances
    print("\n📦 Installation des dépendances...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"])
        print("✅ Dépendances installées")
    except:
        print("⚠️  Échec de l'installation automatique des dépendances")
        print("   Exécutez manuellement: pip install -r requirements.txt")
    
    # Lancement de l'application
    print("\n" + "=" * 60)
    print("🎯 LANCEMENT DE L'APPLICATION")
    print("=" * 60)
    print("\n📊 Application disponible sur: http://localhost:8501")
    print("🔄 Pour arrêter: Ctrl+C")
    print("\n" + "=" * 60)
    
    # Lance Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()