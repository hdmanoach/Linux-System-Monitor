import subprocess
import os

def get_disk_usage_linux(path, top_n=10):
    # ... (code existant) ...

def get_disk_usage_cross_platform(path, top_n=10):
    """
    Obtient les N plus gros fichiers/dossiers pour un chemin donné en utilisant
    des modules Python. C'est plus lent mais multiplateforme.
    """
    try:
        dir_sizes = {}
        # Liste les éléments à la racine du chemin donné
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            total_size = 0
            
            # Si c'est un dossier, on parcourt son contenu
            if os.path.isdir(full_path):
                for dirpath, dirnames, filenames in os.walk(full_path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        try:
                            # Ajoute la taille du fichier au total
                            total_size += os.path.getsize(fp)
                        except OSError:
                            # Ignore les fichiers qu'on ne peut pas lire (permissions, etc.)
                            pass
                dir_sizes[full_path] = total_size
            # Si c'est un fichier, on prend sa taille directement
            elif os.path.isfile(full_path):
                try:
                    dir_sizes[full_path] = os.path.getsize(full_path)
                except OSError:
                    pass

        # Trie les répertoires/fichiers par taille (décroissant)
        sorted_dirs = sorted(dir_sizes.items(), key=lambda item: item[1], reverse=True)

        # Formate le top N pour l'affichage
        top_files = []
        for i, (path, size_bytes) in enumerate(sorted_dirs):
            if i >= top_n:
                break
            
            # Formate la taille pour être lisible
            if size_bytes > 1024 * 1024 * 1024:
                size_formatted = f"{size_bytes / (1024**3):.2f} GB"
            elif size_bytes > 1024 * 1024:
                size_formatted = f"{size_bytes / (1024**2):.2f} MB"
            elif size_bytes > 1024:
                size_formatted = f"{size_bytes / 1024:.2f} KB"
            else:
                size_formatted = f"{size_bytes} B"
            
            top_files.append({"size": size_formatted, "path": path})
            
        return top_files

    except Exception as e:
        print(f"Erreur lors du scan des dossiers : {e}")
        return {"error": "Erreur lors du scan des dossiers", "details": str(e)}

