# core/save_system.py
"""Système de sauvegarde et de chargement complet"""

import json
import pickle
import zlib
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import os

from entities import RunState, Card, CombatState, Biome, Rarity, StatusEffect, Keyword
from progression import ActMap, MapNode, NodeType


class SaveVersion:
    """Gestion des versions de sauvegarde"""
    CURRENT = "1.0.0"
    COMPATIBLE = ["1.0.0", "0.9.0"]  # Versions compatibles


@dataclass
class SaveMetadata:
    """Métadonnées d'une sauvegarde"""
    version: str
    timestamp: str
    run_id: str
    act: int
    node: int
    score: int
    playtime: float  # En secondes
    checksum: str

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'SaveMetadata':
        return cls(**data)


@dataclass
class SaveData:
    """Données complètes d'une sauvegarde"""
    metadata: SaveMetadata
    run_state: Dict
    current_map: Dict
    profile: Dict
    settings: Dict

    def to_dict(self) -> Dict:
        return {
            'metadata': self.metadata.to_dict(),
            'run_state': self.run_state,
            'current_map': self.current_map,
            'profile': self.profile,
            'settings': self.settings
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SaveData':
        return cls(
            metadata=SaveMetadata.from_dict(data['metadata']),
            run_state=data['run_state'],
            current_map=data['current_map'],
            profile=data['profile'],
            settings=data['settings']
        )


class SaveManager:
    """Gestionnaire de sauvegardes"""

    def __init__(self, save_dir: Path = Path("saves")):
        self.save_dir = save_dir
        self.save_dir.mkdir(exist_ok=True)

        # Dossiers spécifiques
        self.runs_dir = self.save_dir / "runs"
        self.profiles_dir = self.save_dir / "profiles"
        self.backup_dir = self.save_dir / "backups"

        for dir_path in [self.runs_dir, self.profiles_dir, self.backup_dir]:
            dir_path.mkdir(exist_ok=True)

        # Cache des sauvegardes
        self._save_cache: Dict[str, SaveData] = {}

        # Configuration de compression
        self.compression_level = 6  # 0-9, 6 est un bon compromis

        # Anti-corruption
        self.enable_checksums = True
        self.enable_backups = True
        self.max_backups = 3

    def save_run(self, run_state: RunState, current_map: ActMap, profile: Dict) -> str:
        """Sauvegarde une run en cours"""

        # Générer un ID unique pour la run
        run_id = self._generate_run_id()

        # Créer les métadonnées
        metadata = SaveMetadata(
            version=SaveVersion.CURRENT,
            timestamp=datetime.now().isoformat(),
            run_id=run_id,
            act=run_state.current_act,
            node=run_state.current_node,
            score=run_state.score,
            playtime=0.0,  # À calculer depuis le début de la run
            checksum=""
        )

        # Sérialiser l'état
        run_data = self._serialize_run_state(run_state)
        map_data = self._serialize_map(current_map)
        settings = self._get_current_settings()

        # Créer le paquet de sauvegarde
        save_data = SaveData(
            metadata=metadata,
            run_state=run_data,
            current_map=map_data,
            profile=profile,
            settings=settings
        )

        # Calculer le checksum
        if self.enable_checksums:
            save_data.metadata.checksum = self._calculate_checksum(save_data)

        # Sauvegarder
        save_path = self.runs_dir / f"{run_id}.sav"
        self._write_save_file(save_path, save_data)

        # Backup automatique
        if self.enable_backups:
            self._create_backup(save_data, run_id)

        # Mettre en cache
        self._save_cache[run_id] = save_data

        return run_id

    def load_run(self, run_id: str) -> Optional[Tuple[RunState, ActMap, Dict]]:
        """Charge une run sauvegardée"""

        # Vérifier le cache
        if run_id in self._save_cache:
            save_data = self._save_cache[run_id]
        else:
            # Charger depuis le disque
            save_path = self.runs_dir / f"{run_id}.sav"
            if not save_path.exists():
                # Essayer de restaurer depuis backup
                save_data = self._restore_from_backup(run_id)
                if not save_data:
                    return None
            else:
                save_data = self._read_save_file(save_path)

        # Vérifier l'intégrité
        if self.enable_checksums:
            if not self._verify_checksum(save_data):
                print(f"⚠️ Checksum invalide pour {run_id}")
                # Essayer le backup
                save_data = self._restore_from_backup(run_id)
                if not save_data:
                    return None

        # Vérifier la compatibilité de version
        if not self._check_version_compatibility(save_data.metadata.version):
            print(f"❌ Version incompatible: {save_data.metadata.version}")
            return None

        # Désérialiser
        run_state = self._deserialize_run_state(save_data.run_state)
        current_map = self._deserialize_map(save_data.current_map)
        profile = save_data.profile

        return run_state, current_map, profile

    def delete_run(self, run_id: str) -> bool:
        """Supprime une sauvegarde de run"""
        save_path = self.runs_dir / f"{run_id}.sav"

        if save_path.exists():
            # Créer un backup avant suppression
            if self.enable_backups:
                save_data = self._read_save_file(save_path)
                self._create_backup(save_data, run_id, prefix="deleted_")

            save_path.unlink()

            # Nettoyer le cache
            if run_id in self._save_cache:
                del self._save_cache[run_id]

            return True

        return False

    def list_saves(self) -> List[SaveMetadata]:
        """Liste toutes les sauvegardes disponibles"""
        saves = []

        for save_file in self.runs_dir.glob("*.sav"):
            try:
                save_data = self._read_save_file(save_file)
                saves.append(save_data.metadata)
            except Exception as e:
                print(f"⚠️ Impossible de lire {save_file}: {e}")

        # Trier par date
        saves.sort(key=lambda s: s.timestamp, reverse=True)

        return saves

    def save_profile(self, profile: Dict) -> bool:
        """Sauvegarde le profil du joueur"""
        profile_path = self.profiles_dir / "profile.json"

        # Backup du profil existant
        if profile_path.exists() and self.enable_backups:
            backup_path = self.backup_dir / f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(profile_path, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())

        # Sauvegarder
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2)

        return True

    def load_profile(self) -> Dict:
        """Charge le profil du joueur"""
        profile_path = self.profiles_dir / "profile.json"

        if profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Profil par défaut
        return {
            'total_runs': 0,
            'victories': 0,
            'unlocked_cards': [],
            'trophies': 0,
            'achievements': [],
            'statistics': {}
        }

    def _serialize_run_state(self, run_state: RunState) -> Dict:
        """Sérialise l'état d'une run"""
        return {
            'deck': [self._serialize_card(card) for card in run_state.current_deck],
            'current_node': run_state.current_node,
            'current_act': run_state.current_act,
            'fragments': run_state.fragments,
            'genes': run_state.genes,
            'eggs': run_state.eggs,
            'trophies': run_state.trophies,
            'unlocked_cards': list(run_state.unlocked_cards),
            'visited_nodes': run_state.visited_nodes,
            'score': run_state.score
        }

    def _deserialize_run_state(self, data: Dict) -> RunState:
        """Désérialise l'état d'une run"""
        run_state = RunState(
            current_deck=[self._deserialize_card(card_data) for card_data in data['deck']]
        )

        run_state.current_node = data['current_node']
        run_state.current_act = data['current_act']
        run_state.fragments = data['fragments']
        run_state.genes = data['genes']
        run_state.eggs = data['eggs']
        run_state.trophies = data['trophies']
        run_state.unlocked_cards = set(data['unlocked_cards'])
        run_state.visited_nodes = data['visited_nodes']
        run_state.score = data['score']

        return run_state

    def _serialize_card(self, card: Card) -> Dict:
        """Sérialise une carte avec son état permanent"""
        return {
            'id': card.id,
            'name': card.name,
            'biome': card.biome.value,
            'rarity': card.rarity.value,
            'cost': card.cost,
            'base_stats': {
                'atk': card.base_atk,
                'dur': card.base_dur,
                'spd': card.base_spd
            },
            'current_stats': {
                'atk': card.current_atk,
                'dur': card.current_dur,
                'spd': card.current_spd
            },
            'shields': card.shields,
            'keywords': [k.name for k in card.keywords],
            'statuses': {s.value: v for s, v in card.permanent_statuses.items()},
            'on_deploy': card.on_deploy,
            'on_attack': card.on_attack,
            'on_hit': card.on_hit,
            'on_death': card.on_death
        }

    def _deserialize_card(self, data: Dict) -> Card:
        """Désérialise une carte"""
        card = Card(
            id=data['id'],
            name=data['name'],
            biome=Biome(data['biome']),
            rarity=Rarity(data['rarity']),
            cost=data['cost'],
            base_atk=data['base_stats']['atk'],
            base_dur=data['base_stats']['dur'],
            base_spd=data['base_stats']['spd']
        )

        # Restaurer l'état actuel
        card.current_atk = data['current_stats']['atk']
        card.current_dur = data['current_stats']['dur']
        card.current_spd = data['current_stats']['spd']
        card.shields = data.get('shields', 0)

        # Keywords
        for k_name in data.get('keywords', []):
            card.keywords.add(Keyword[k_name])

        # Statuts permanents
        for status_name, value in data.get('statuses', {}).items():
            card.permanent_statuses[StatusEffect(status_name)] = value

        # Capacités
        card.on_deploy = data.get('on_deploy', [])
        card.on_attack = data.get('on_attack', [])
        card.on_hit = data.get('on_hit', [])
        card.on_death = data.get('on_death', [])

        return card

    def _serialize_map(self, act_map: ActMap) -> Dict:
        """Sérialise une carte d'acte"""
        return {
            'act_number': act_map.act_number,
            'biome': act_map.biome.value,
            'current_node': act_map.current_node,
            'boss_node': act_map.boss_node,
            'nodes': [self._serialize_node(node) for node in act_map.nodes]
        }

    def _deserialize_map(self, data: Dict) -> ActMap:
        """Désérialise une carte d'acte"""
        act_map = ActMap(
            act_number=data['act_number'],
            biome=Biome(data['biome']),
            nodes=[self._deserialize_node(node_data) for node_data in data['nodes']]
        )

        act_map.current_node = data['current_node']
        act_map.boss_node = data.get('boss_node')

        return act_map

    def _serialize_node(self, node: MapNode) -> Dict:
        """Sérialise un nœud de carte"""
        return {
            'id': node.id,
            'type': node.node_type.value,
            'biome': node.biome.value,
            'x': node.x,
            'y': node.y,
            'connections': node.connections,
            'visited': node.visited,
            'revealed': node.revealed,
            'enemy_pool': node.enemy_pool,
            'rewards': node.rewards,
            'event_data': node.event_data
        }

    def _deserialize_node(self, data: Dict) -> MapNode:
        """Désérialise un nœud de carte"""
        return MapNode(
            id=data['id'],
            node_type=NodeType(data['type']),
            biome=Biome(data['biome']),
            x=data['x'],
            y=data['y'],
            connections=data['connections'],
            visited=data['visited'],
            revealed=data['revealed'],
            enemy_pool=data.get('enemy_pool', []),
            rewards=data.get('rewards', {}),
            event_data=data.get('event_data')
        )

    def _write_save_file(self, path: Path, save_data: SaveData):
        """Écrit un fichier de sauvegarde avec compression"""

        # Convertir en JSON
        json_data = json.dumps(save_data.to_dict(), separators=(',', ':'))

        # Compresser
        compressed = zlib.compress(json_data.encode('utf-8'), self.compression_level)

        # Encoder en base64 pour éviter les problèmes de caractères
        encoded = base64.b64encode(compressed)

        # Écrire
        with open(path, 'wb') as f:
            f.write(encoded)

    def _read_save_file(self, path: Path) -> SaveData:
        """Lit un fichier de sauvegarde compressé"""

        with open(path, 'rb') as f:
            encoded = f.read()

        # Décoder depuis base64
        compressed = base64.b64decode(encoded)

        # Décompresser
        json_data = zlib.decompress(compressed).decode('utf-8')

        # Parser JSON
        data = json.loads(json_data)

        return SaveData.from_dict(data)

    def _calculate_checksum(self, save_data: SaveData) -> str:
        """Calcule un checksum pour vérifier l'intégrité"""
        # Exclure le checksum lui-même du calcul
        data_copy = save_data.to_dict()
        data_copy['metadata']['checksum'] = ""

        # Calculer SHA256
        json_str = json.dumps(data_copy, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def _verify_checksum(self, save_data: SaveData) -> bool:
        """Vérifie l'intégrité d'une sauvegarde"""
        expected = save_data.metadata.checksum
        actual = self._calculate_checksum(save_data)
        return expected == actual

    def _create_backup(self, save_data: SaveData, run_id: str, prefix: str = ""):
        """Crée un backup d'une sauvegarde"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f"{prefix}{run_id}_{timestamp}.bak"

        self._write_save_file(backup_path, save_data)

        # Nettoyer les vieux backups
        self._cleanup_old_backups(run_id)

    def _restore_from_backup(self, run_id: str) -> Optional[SaveData]:
        """Restaure depuis un backup"""
        # Chercher le backup le plus récent
        backups = list(self.backup_dir.glob(f"*{run_id}*.bak"))

        if not backups:
            return None

        # Trier par date de modification
        backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Essayer de charger le plus récent
        for backup_path in backups:
            try:
                save_data = self._read_save_file(backup_path)
                print(f"✅ Restauré depuis backup: {backup_path.name}")
                return save_data
            except Exception as e:
                print(f"⚠️ Backup corrompu {backup_path.name}: {e}")

        return None

    def _cleanup_old_backups(self, run_id: str):
        """Nettoie les vieux backups"""
        backups = list(self.backup_dir.glob(f"*{run_id}*.bak"))

        if len(backups) > self.max_backups:
            # Trier par date
            backups.sort(key=lambda p: p.stat().st_mtime)

            # Supprimer les plus vieux
            for backup in backups[:-self.max_backups]:
                backup.unlink()

    def _check_version_compatibility(self, version: str) -> bool:
        """Vérifie la compatibilité de version"""
        return version in SaveVersion.COMPATIBLE

    def _generate_run_id(self) -> str:
        """Génère un ID unique pour une run"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = os.urandom(4).hex()
        return f"run_{timestamp}_{random_part}"

    def _get_current_settings(self) -> Dict:
        """Récupère les paramètres actuels du jeu"""
        # À implémenter selon votre système de configuration
        return {
            'difficulty': 'normal',
            'sound_enabled': True,
            'music_volume': 0.7,
            'sfx_volume': 0.8
        }

    def export_save(self, run_id: str, export_path: Path) -> bool:
        """Exporte une sauvegarde pour partage"""
        save_path = self.runs_dir / f"{run_id}.sav"

        if not save_path.exists():
            return False

        # Copier le fichier
        import shutil
        shutil.copy2(save_path, export_path)

        print(f"✅ Sauvegarde exportée: {export_path}")
        return True

    def import_save(self, import_path: Path) -> Optional[str]:
        """Importe une sauvegarde externe"""
        try:
            # Lire et valider
            save_data = self._read_save_file(import_path)

            # Vérifier la version
            if not self._check_version_compatibility(save_data.metadata.version):
                print("❌ Version incompatible")
                return None

            # Générer un nouvel ID
            new_id = self._generate_run_id()
            save_data.metadata.run_id = new_id

            # Sauvegarder
            save_path = self.runs_dir / f"{new_id}.sav"
            self._write_save_file(save_path, save_data)

            print(f"✅ Sauvegarde importée: {new_id}")
            return new_id

        except Exception as e:
            print(f"❌ Erreur d'import: {e}")
            return None