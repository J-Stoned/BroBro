"""
Enhancement 9: Workflow Version Control System
Git-like version control for workflows with branches, commits, and merging
"""
import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class WorkflowVersionControl:
    """
    Git-like version control system for workflows

    Features:
    - Commits with messages and metadata
    - Branching and merging
    - Diff calculation
    - Version history
    - Tags/labels
    - Conflict detection
    """

    def __init__(self, db_path: str = "workflow_versions.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Commits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commits (
                id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                branch TEXT NOT NULL,
                parent_commit_id TEXT,
                commit_message TEXT NOT NULL,
                author TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                workflow_snapshot TEXT NOT NULL,
                metadata TEXT
            )
        """)

        # Branches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS branches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                name TEXT NOT NULL,
                head_commit_id TEXT,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                UNIQUE(workflow_id, name)
            )
        """)

        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                name TEXT NOT NULL,
                commit_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                description TEXT,
                UNIQUE(workflow_id, name)
            )
        """)

        # Workflow metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                current_branch TEXT DEFAULT 'main',
                created_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def create_workflow(self, workflow_id: str, name: str) -> Dict:
        """Create a new workflow with version control"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()

        try:
            # Create workflow record
            cursor.execute(
                "INSERT INTO workflows (id, name, current_branch, created_at) VALUES (?, ?, ?, ?)",
                (workflow_id, name, 'main', now)
            )

            # Create main branch
            cursor.execute(
                "INSERT INTO branches (workflow_id, name, created_at, created_by) VALUES (?, ?, ?, ?)",
                (workflow_id, 'main', now, 'system')
            )

            conn.commit()
            return {'success': True, 'workflow_id': workflow_id, 'branch': 'main'}

        except sqlite3.IntegrityError as e:
            conn.rollback()
            return {'success': False, 'error': f'Workflow already exists: {str(e)}'}

        finally:
            conn.close()

    def commit(
        self,
        workflow_id: str,
        workflow_data: Dict,
        message: str,
        author: str,
        branch: str = 'main'
    ) -> Dict:
        """
        Create a new commit

        Args:
            workflow_id: Unique workflow identifier
            workflow_data: Complete workflow state
            message: Commit message
            author: Author name/email
            branch: Branch name (default: 'main')

        Returns:
            Dict with success status and commit_id
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get current head of branch
            cursor.execute(
                "SELECT head_commit_id FROM branches WHERE workflow_id = ? AND name = ?",
                (workflow_id, branch)
            )
            result = cursor.fetchone()

            if not result:
                return {'success': False, 'error': f'Branch {branch} not found'}

            parent_commit_id = result[0]

            # Generate commit hash
            now = datetime.utcnow().isoformat()
            workflow_json = json.dumps(workflow_data, sort_keys=True)
            commit_content = f"{workflow_id}{branch}{parent_commit_id}{message}{author}{now}{workflow_json}"
            commit_id = hashlib.sha256(commit_content.encode()).hexdigest()[:12]

            # Create commit
            cursor.execute("""
                INSERT INTO commits (
                    id, workflow_id, branch, parent_commit_id,
                    commit_message, author, timestamp, workflow_snapshot
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (commit_id, workflow_id, branch, parent_commit_id, message, author, now, workflow_json))

            # Update branch head
            cursor.execute(
                "UPDATE branches SET head_commit_id = ? WHERE workflow_id = ? AND name = ?",
                (commit_id, workflow_id, branch)
            )

            conn.commit()
            return {
                'success': True,
                'commit_id': commit_id,
                'branch': branch,
                'timestamp': now
            }

        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}

        finally:
            conn.close()

    def get_history(self, workflow_id: str, branch: str = 'main', limit: int = 50) -> List[Dict]:
        """Get commit history for a branch"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get branch head
            cursor.execute(
                "SELECT head_commit_id FROM branches WHERE workflow_id = ? AND name = ?",
                (workflow_id, branch)
            )
            result = cursor.fetchone()

            if not result or not result[0]:
                return []

            # Walk commit history
            history = []
            current_commit_id = result[0]

            while current_commit_id and len(history) < limit:
                cursor.execute("""
                    SELECT id, commit_message, author, timestamp, parent_commit_id, metadata
                    FROM commits
                    WHERE id = ?
                """, (current_commit_id,))

                commit = cursor.fetchone()
                if not commit:
                    break

                history.append({
                    'commit_id': commit[0],
                    'message': commit[1],
                    'author': commit[2],
                    'timestamp': commit[3],
                    'parent': commit[4],
                    'metadata': json.loads(commit[5]) if commit[5] else {}
                })

                current_commit_id = commit[4]

            return history

        finally:
            conn.close()

    def get_commit(self, commit_id: str) -> Optional[Dict]:
        """Get complete commit data including workflow snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, workflow_id, branch, parent_commit_id,
                       commit_message, author, timestamp, workflow_snapshot, metadata
                FROM commits
                WHERE id = ?
            """, (commit_id,))

            result = cursor.fetchone()
            if not result:
                return None

            return {
                'commit_id': result[0],
                'workflow_id': result[1],
                'branch': result[2],
                'parent': result[3],
                'message': result[4],
                'author': result[5],
                'timestamp': result[6],
                'workflow': json.loads(result[7]),
                'metadata': json.loads(result[8]) if result[8] else {}
            }

        finally:
            conn.close()

    def create_branch(
        self,
        workflow_id: str,
        branch_name: str,
        from_branch: str = 'main',
        author: str = 'system'
    ) -> Dict:
        """Create a new branch from existing branch"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get head commit of source branch
            cursor.execute(
                "SELECT head_commit_id FROM branches WHERE workflow_id = ? AND name = ?",
                (workflow_id, from_branch)
            )
            result = cursor.fetchone()

            if not result:
                return {'success': False, 'error': f'Source branch {from_branch} not found'}

            head_commit = result[0]
            now = datetime.utcnow().isoformat()

            # Create new branch
            cursor.execute("""
                INSERT INTO branches (workflow_id, name, head_commit_id, created_at, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (workflow_id, branch_name, head_commit, now, author))

            conn.commit()
            return {
                'success': True,
                'branch': branch_name,
                'head_commit': head_commit
            }

        except sqlite3.IntegrityError:
            conn.rollback()
            return {'success': False, 'error': f'Branch {branch_name} already exists'}

        finally:
            conn.close()

    def list_branches(self, workflow_id: str) -> List[Dict]:
        """List all branches for a workflow"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT name, head_commit_id, created_at, created_by
                FROM branches
                WHERE workflow_id = ?
                ORDER BY created_at DESC
            """, (workflow_id,))

            branches = []
            for row in cursor.fetchall():
                branches.append({
                    'name': row[0],
                    'head_commit': row[1],
                    'created_at': row[2],
                    'created_by': row[3]
                })

            return branches

        finally:
            conn.close()

    def calculate_diff(self, commit_id_a: str, commit_id_b: str) -> Dict:
        """Calculate difference between two commits"""
        commit_a = self.get_commit(commit_id_a)
        commit_b = self.get_commit(commit_id_b)

        if not commit_a or not commit_b:
            return {'success': False, 'error': 'Commit not found'}

        workflow_a = commit_a['workflow']
        workflow_b = commit_b['workflow']

        # Calculate node differences
        nodes_a = {node['id']: node for node in workflow_a.get('nodes', [])}
        nodes_b = {node['id']: node for node in workflow_b.get('nodes', [])}

        added_nodes = [nodes_b[nid] for nid in nodes_b if nid not in nodes_a]
        removed_nodes = [nodes_a[nid] for nid in nodes_a if nid not in nodes_b]
        modified_nodes = []

        for node_id in nodes_a:
            if node_id in nodes_b:
                if nodes_a[node_id] != nodes_b[node_id]:
                    modified_nodes.append({
                        'id': node_id,
                        'before': nodes_a[node_id],
                        'after': nodes_b[node_id]
                    })

        # Calculate connection differences
        conns_a = set((c.get('source'), c.get('target')) for c in workflow_a.get('connections', []))
        conns_b = set((c.get('source'), c.get('target')) for c in workflow_b.get('connections', []))

        added_connections = list(conns_b - conns_a)
        removed_connections = list(conns_a - conns_b)

        return {
            'success': True,
            'added_nodes': added_nodes,
            'removed_nodes': removed_nodes,
            'modified_nodes': modified_nodes,
            'added_connections': added_connections,
            'removed_connections': removed_connections,
            'summary': {
                'nodes_added': len(added_nodes),
                'nodes_removed': len(removed_nodes),
                'nodes_modified': len(modified_nodes),
                'connections_added': len(added_connections),
                'connections_removed': len(removed_connections)
            }
        }

    def merge_branches(
        self,
        workflow_id: str,
        source_branch: str,
        target_branch: str,
        author: str,
        strategy: str = 'auto'
    ) -> Dict:
        """
        Merge source branch into target branch

        Strategies:
        - 'auto': Automatic merge if no conflicts
        - 'ours': Keep target branch changes
        - 'theirs': Take source branch changes
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get head commits of both branches
            cursor.execute("""
                SELECT name, head_commit_id
                FROM branches
                WHERE workflow_id = ? AND name IN (?, ?)
            """, (workflow_id, source_branch, target_branch))

            branches = {row[0]: row[1] for row in cursor.fetchall()}

            if source_branch not in branches or target_branch not in branches:
                return {'success': False, 'error': 'Branch not found'}

            source_commit = self.get_commit(branches[source_branch])
            target_commit = self.get_commit(branches[target_branch])

            # Calculate diff
            diff = self.calculate_diff(branches[target_branch], branches[source_branch])

            # Check for conflicts
            conflicts = self._detect_conflicts(diff)

            if conflicts and strategy == 'auto':
                return {
                    'success': False,
                    'conflict': True,
                    'conflicts': conflicts,
                    'message': 'Merge conflicts detected. Choose merge strategy.'
                }

            # Perform merge based on strategy
            if strategy == 'theirs':
                merged_workflow = source_commit['workflow']
            elif strategy == 'ours':
                merged_workflow = target_commit['workflow']
            else:
                # Auto merge (no conflicts)
                merged_workflow = self._auto_merge(target_commit['workflow'], diff)

            # Create merge commit
            merge_message = f"Merge branch '{source_branch}' into '{target_branch}'"
            commit_result = self.commit(
                workflow_id=workflow_id,
                workflow_data=merged_workflow,
                message=merge_message,
                author=author,
                branch=target_branch
            )

            if commit_result['success']:
                return {
                    'success': True,
                    'commit_id': commit_result['commit_id'],
                    'message': merge_message
                }
            else:
                return commit_result

        except Exception as e:
            return {'success': False, 'error': str(e)}

        finally:
            conn.close()

    def _detect_conflicts(self, diff: Dict) -> List[Dict]:
        """Detect merge conflicts in diff"""
        conflicts = []

        # Modified nodes are potential conflicts
        for modified in diff.get('modified_nodes', []):
            conflicts.append({
                'type': 'node_modification',
                'node_id': modified['id'],
                'description': f"Node '{modified['id']}' was modified in both branches"
            })

        return conflicts

    def _auto_merge(self, base_workflow: Dict, diff: Dict) -> Dict:
        """Automatically merge changes when no conflicts"""
        merged = base_workflow.copy()

        # Apply added nodes
        nodes = {node['id']: node for node in merged.get('nodes', [])}
        for added_node in diff.get('added_nodes', []):
            nodes[added_node['id']] = added_node

        # Remove deleted nodes
        for removed_node in diff.get('removed_nodes', []):
            nodes.pop(removed_node['id'], None)

        merged['nodes'] = list(nodes.values())

        # Apply connection changes
        connections = set((c.get('source'), c.get('target')) for c in merged.get('connections', []))
        for added_conn in diff.get('added_connections', []):
            connections.add(added_conn)
        for removed_conn in diff.get('removed_connections', []):
            connections.discard(removed_conn)

        merged['connections'] = [
            {'source': src, 'target': tgt}
            for src, tgt in connections
        ]

        return merged

    def create_tag(
        self,
        workflow_id: str,
        tag_name: str,
        commit_id: str,
        author: str,
        description: str = ''
    ) -> Dict:
        """Create a tag/label for a specific commit"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            now = datetime.utcnow().isoformat()
            cursor.execute("""
                INSERT INTO tags (workflow_id, name, commit_id, created_at, created_by, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (workflow_id, tag_name, commit_id, now, author, description))

            conn.commit()
            return {'success': True, 'tag': tag_name, 'commit': commit_id}

        except sqlite3.IntegrityError:
            return {'success': False, 'error': f'Tag {tag_name} already exists'}

        finally:
            conn.close()

    def list_tags(self, workflow_id: str) -> List[Dict]:
        """List all tags for a workflow"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT name, commit_id, created_at, created_by, description
                FROM tags
                WHERE workflow_id = ?
                ORDER BY created_at DESC
            """, (workflow_id,))

            tags = []
            for row in cursor.fetchall():
                tags.append({
                    'name': row[0],
                    'commit_id': row[1],
                    'created_at': row[2],
                    'created_by': row[3],
                    'description': row[4]
                })

            return tags

        finally:
            conn.close()

# Singleton instance
version_control = WorkflowVersionControl()
