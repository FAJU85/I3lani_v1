#!/usr/bin/env python3
"""
Sequence System Dashboard
Comprehensive monitoring and debugging interface for sequence tracking
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from sequence_system import get_sequence_system, SequenceType, SequenceStatus
from sequence_integration import get_sequence_integration

logger = logging.getLogger(__name__)

class SequenceDashboard:
    """Dashboard for monitoring and managing sequence system"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.sequence_system = get_sequence_system()
        self.sequence_integration = get_sequence_integration()
    
    def show_system_overview(self) -> Dict:
        """Show comprehensive system overview"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get overall statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sequences,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_sequences,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_sequences,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_sequences,
                    AVG(progress_percentage) as avg_progress,
                    MAX(updated_at) as last_activity
                FROM sequences
            """)
            
            stats = cursor.fetchone()
            
            # Get sequence type distribution
            cursor.execute("""
                SELECT sequence_type, COUNT(*) as count, 
                       AVG(progress_percentage) as avg_progress
                FROM sequences
                GROUP BY sequence_type
                ORDER BY count DESC
            """)
            
            type_distribution = cursor.fetchall()
            
            # Get component health
            cursor.execute("""
                SELECT component, 
                       COUNT(*) as total_steps,
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_steps,
                       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_steps,
                       SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_steps
                FROM sequence_steps
                GROUP BY component
                ORDER BY total_steps DESC
            """)
            
            component_health = cursor.fetchall()
            
            # Get recent activity
            cursor.execute("""
                SELECT sequence_id, sequence_type, user_id, current_step, 
                       progress_percentage, updated_at
                FROM sequences
                ORDER BY updated_at DESC
                LIMIT 10
            """)
            
            recent_activity = cursor.fetchall()
            
            return {
                'overview': {
                    'total_sequences': stats[0] or 0,
                    'active_sequences': stats[1] or 0,
                    'completed_sequences': stats[2] or 0,
                    'failed_sequences': stats[3] or 0,
                    'average_progress': round(stats[4] or 0, 1),
                    'last_activity': stats[5]
                },
                'type_distribution': [
                    {
                        'type': dist[0],
                        'count': dist[1],
                        'avg_progress': round(dist[2], 1)
                    } for dist in type_distribution
                ],
                'component_health': [
                    {
                        'component': comp[0],
                        'total_steps': comp[1],
                        'completed_steps': comp[2],
                        'failed_steps': comp[3],
                        'in_progress_steps': comp[4],
                        'success_rate': round((comp[2] / comp[1]) * 100, 1) if comp[1] > 0 else 0
                    } for comp in component_health
                ],
                'recent_activity': [
                    {
                        'sequence_id': act[0],
                        'type': act[1],
                        'user_id': act[2],
                        'current_step': act[3],
                        'progress': act[4],
                        'updated_at': act[5]
                    } for act in recent_activity
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system overview: {e}")
            return {}
        finally:
            conn.close()
    
    def show_user_sequences(self, user_id: int) -> Dict:
        """Show all sequences for a specific user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user's sequences
            cursor.execute("""
                SELECT sequence_id, sequence_type, status, current_step,
                       progress_percentage, created_at, updated_at, completed_at
                FROM sequences
                WHERE user_id = ?
                ORDER BY updated_at DESC
            """, (user_id,))
            
            sequences = cursor.fetchall()
            
            user_sequences = []
            for seq in sequences:
                # Get sequence steps
                cursor.execute("""
                    SELECT step_name, status, started_at, completed_at, error_message
                    FROM sequence_steps
                    WHERE sequence_id = ?
                    ORDER BY step_order
                """, (seq[0],))
                
                steps = cursor.fetchall()
                
                user_sequences.append({
                    'sequence_id': seq[0],
                    'type': seq[1],
                    'status': seq[2],
                    'current_step': seq[3],
                    'progress': seq[4],
                    'created_at': seq[5],
                    'updated_at': seq[6],
                    'completed_at': seq[7],
                    'steps': [
                        {
                            'name': step[0],
                            'status': step[1],
                            'started_at': step[2],
                            'completed_at': step[3],
                            'error_message': step[4]
                        } for step in steps
                    ]
                })
            
            return {
                'user_id': user_id,
                'total_sequences': len(sequences),
                'sequences': user_sequences
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user sequences: {e}")
            return {}
        finally:
            conn.close()
    
    def show_sequence_details(self, sequence_id: str) -> Dict:
        """Show detailed information about a specific sequence"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get sequence info
            cursor.execute("""
                SELECT sequence_type, user_id, entity_id, status, current_step,
                       progress_percentage, metadata, created_at, updated_at, completed_at
                FROM sequences
                WHERE sequence_id = ?
            """, (sequence_id,))
            
            seq_info = cursor.fetchone()
            if not seq_info:
                return {'error': 'Sequence not found'}
            
            # Get sequence steps
            cursor.execute("""
                SELECT step_name, step_description, component, step_order, status,
                       started_at, completed_at, error_message, metadata
                FROM sequence_steps
                WHERE sequence_id = ?
                ORDER BY step_order
            """, (sequence_id,))
            
            steps = cursor.fetchall()
            
            # Get component links
            cursor.execute("""
                SELECT component_name, entity_type, entity_id, link_type, created_at
                FROM component_links
                WHERE sequence_id = ?
            """, (sequence_id,))
            
            links = cursor.fetchall()
            
            # Get flow transitions
            cursor.execute("""
                SELECT from_step, to_step, transition_time, trigger_event, metadata
                FROM flow_transitions
                WHERE sequence_id = ?
                ORDER BY transition_time
            """, (sequence_id,))
            
            transitions = cursor.fetchall()
            
            return {
                'sequence_info': {
                    'sequence_id': sequence_id,
                    'type': seq_info[0],
                    'user_id': seq_info[1],
                    'entity_id': seq_info[2],
                    'status': seq_info[3],
                    'current_step': seq_info[4],
                    'progress': seq_info[5],
                    'metadata': json.loads(seq_info[6]) if seq_info[6] else {},
                    'created_at': seq_info[7],
                    'updated_at': seq_info[8],
                    'completed_at': seq_info[9]
                },
                'steps': [
                    {
                        'name': step[0],
                        'description': step[1],
                        'component': step[2],
                        'order': step[3],
                        'status': step[4],
                        'started_at': step[5],
                        'completed_at': step[6],
                        'error_message': step[7],
                        'metadata': json.loads(step[8]) if step[8] else {}
                    } for step in steps
                ],
                'component_links': [
                    {
                        'component': link[0],
                        'entity_type': link[1],
                        'entity_id': link[2],
                        'link_type': link[3],
                        'created_at': link[4]
                    } for link in links
                ],
                'flow_transitions': [
                    {
                        'from_step': trans[0],
                        'to_step': trans[1],
                        'time': trans[2],
                        'trigger': trans[3],
                        'metadata': json.loads(trans[4]) if trans[4] else {}
                    } for trans in transitions
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting sequence details: {e}")
            return {'error': str(e)}
        finally:
            conn.close()
    
    def find_stuck_sequences(self, hours_threshold: int = 1) -> List[Dict]:
        """Find sequences that appear to be stuck"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            threshold_time = datetime.now() - timedelta(hours=hours_threshold)
            
            cursor.execute("""
                SELECT sequence_id, sequence_type, user_id, current_step,
                       progress_percentage, updated_at
                FROM sequences
                WHERE status = 'active' 
                AND updated_at < ?
                ORDER BY updated_at
            """, (threshold_time.isoformat(),))
            
            stuck_sequences = cursor.fetchall()
            
            result = []
            for seq in stuck_sequences:
                # Get last completed step
                cursor.execute("""
                    SELECT step_name, completed_at, error_message
                    FROM sequence_steps
                    WHERE sequence_id = ? AND status = 'completed'
                    ORDER BY step_order DESC
                    LIMIT 1
                """, (seq[0],))
                
                last_step = cursor.fetchone()
                
                # Calculate stuck duration
                last_updated = datetime.fromisoformat(seq[5])
                stuck_duration = (datetime.now() - last_updated).total_seconds() / 3600
                
                result.append({
                    'sequence_id': seq[0],
                    'type': seq[1],
                    'user_id': seq[2],
                    'current_step': seq[3],
                    'progress': seq[4],
                    'last_updated': seq[5],
                    'stuck_duration_hours': round(stuck_duration, 1),
                    'last_completed_step': last_step[0] if last_step else None,
                    'last_step_completed_at': last_step[1] if last_step else None,
                    'last_error': last_step[2] if last_step else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error finding stuck sequences: {e}")
            return []
        finally:
            conn.close()
    
    def find_failed_sequences(self, hours_recent: int = 24) -> List[Dict]:
        """Find recent failed sequences"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            threshold_time = datetime.now() - timedelta(hours=hours_recent)
            
            cursor.execute("""
                SELECT s.sequence_id, s.sequence_type, s.user_id, s.current_step,
                       s.progress_percentage, s.updated_at
                FROM sequences s
                WHERE s.status = 'failed' 
                AND s.updated_at > ?
                ORDER BY s.updated_at DESC
            """, (threshold_time.isoformat(),))
            
            failed_sequences = cursor.fetchall()
            
            result = []
            for seq in failed_sequences:
                # Get failed steps
                cursor.execute("""
                    SELECT step_name, error_message, completed_at
                    FROM sequence_steps
                    WHERE sequence_id = ? AND status = 'failed'
                    ORDER BY step_order
                """, (seq[0],))
                
                failed_steps = cursor.fetchall()
                
                result.append({
                    'sequence_id': seq[0],
                    'type': seq[1],
                    'user_id': seq[2],
                    'current_step': seq[3],
                    'progress': seq[4],
                    'failed_at': seq[5],
                    'failed_steps': [
                        {
                            'step_name': step[0],
                            'error_message': step[1],
                            'failed_at': step[2]
                        } for step in failed_steps
                    ]
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error finding failed sequences: {e}")
            return []
        finally:
            conn.close()
    
    def get_component_performance(self, component_name: str) -> Dict:
        """Get performance metrics for a specific component"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get component step statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_steps,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_steps,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_steps,
                    SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_steps,
                    AVG(CASE WHEN status = 'completed' AND started_at IS NOT NULL AND completed_at IS NOT NULL
                        THEN (julianday(completed_at) - julianday(started_at)) * 86400 ELSE NULL END) as avg_duration_seconds
                FROM sequence_steps
                WHERE component = ?
            """, (component_name,))
            
            stats = cursor.fetchone()
            
            # Get recent errors
            cursor.execute("""
                SELECT step_name, error_message, completed_at
                FROM sequence_steps
                WHERE component = ? AND status = 'failed'
                ORDER BY completed_at DESC
                LIMIT 10
            """, (component_name,))
            
            recent_errors = cursor.fetchall()
            
            # Get step type distribution
            cursor.execute("""
                SELECT step_name, COUNT(*) as count,
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM sequence_steps
                WHERE component = ?
                GROUP BY step_name
                ORDER BY count DESC
            """, (component_name,))
            
            step_distribution = cursor.fetchall()
            
            return {
                'component_name': component_name,
                'statistics': {
                    'total_steps': stats[0] or 0,
                    'completed_steps': stats[1] or 0,
                    'failed_steps': stats[2] or 0,
                    'in_progress_steps': stats[3] or 0,
                    'success_rate': round((stats[1] / stats[0]) * 100, 1) if stats[0] > 0 else 0,
                    'average_duration_seconds': round(stats[4], 2) if stats[4] else 0
                },
                'recent_errors': [
                    {
                        'step_name': error[0],
                        'error_message': error[1],
                        'failed_at': error[2]
                    } for error in recent_errors
                ],
                'step_distribution': [
                    {
                        'step_name': step[0],
                        'total_count': step[1],
                        'completed_count': step[2],
                        'failed_count': step[3],
                        'success_rate': round((step[2] / step[1]) * 100, 1) if step[1] > 0 else 0
                    } for step in step_distribution
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting component performance: {e}")
            return {}
        finally:
            conn.close()
    
    def trace_entity_flow(self, entity_type: str, entity_id: str) -> List[Dict]:
        """Trace the complete flow of an entity through the system"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find all sequences linked to this entity
            cursor.execute("""
                SELECT DISTINCT cl.sequence_id, s.sequence_type, s.user_id, s.status,
                       s.progress_percentage, s.created_at, s.updated_at
                FROM component_links cl
                JOIN sequences s ON cl.sequence_id = s.sequence_id
                WHERE cl.entity_type = ? AND cl.entity_id = ?
                ORDER BY s.created_at
            """, (entity_type, entity_id))
            
            linked_sequences = cursor.fetchall()
            
            entity_flow = []
            for seq in linked_sequences:
                # Get sequence steps
                cursor.execute("""
                    SELECT step_name, status, started_at, completed_at, error_message
                    FROM sequence_steps
                    WHERE sequence_id = ?
                    ORDER BY step_order
                """, (seq[0],))
                
                steps = cursor.fetchall()
                
                entity_flow.append({
                    'sequence_id': seq[0],
                    'type': seq[1],
                    'user_id': seq[2],
                    'status': seq[3],
                    'progress': seq[4],
                    'created_at': seq[5],
                    'updated_at': seq[6],
                    'steps': [
                        {
                            'name': step[0],
                            'status': step[1],
                            'started_at': step[2],
                            'completed_at': step[3],
                            'error_message': step[4]
                        } for step in steps
                    ]
                })
            
            return {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'total_sequences': len(linked_sequences),
                'flow': entity_flow
            }
            
        except Exception as e:
            logger.error(f"❌ Error tracing entity flow: {e}")
            return {}
        finally:
            conn.close()
    
    def generate_health_report(self) -> Dict:
        """Generate comprehensive system health report"""
        overview = self.show_system_overview()
        stuck_sequences = self.find_stuck_sequences()
        failed_sequences = self.find_failed_sequences()
        
        # Get component performance for all components
        components = []
        if overview.get('component_health'):
            for comp in overview['component_health']:
                comp_perf = self.get_component_performance(comp['component'])
                components.append(comp_perf)
        
        return {
            'generated_at': datetime.now().isoformat(),
            'system_overview': overview,
            'stuck_sequences': stuck_sequences,
            'failed_sequences': failed_sequences,
            'component_performance': components,
            'recommendations': self._generate_recommendations(overview, stuck_sequences, failed_sequences)
        }
    
    def _generate_recommendations(self, overview: Dict, stuck_sequences: List, 
                                failed_sequences: List) -> List[str]:
        """Generate recommendations based on system health"""
        recommendations = []
        
        if stuck_sequences:
            recommendations.append(f"🔄 {len(stuck_sequences)} sequences appear stuck - consider manual intervention")
        
        if failed_sequences:
            recommendations.append(f"❌ {len(failed_sequences)} sequences failed recently - investigate error patterns")
        
        if overview.get('overview', {}).get('average_progress', 0) < 50:
            recommendations.append("📊 Low average progress - check for bottlenecks in sequence flows")
        
        active_count = overview.get('overview', {}).get('active_sequences', 0)
        if active_count > 100:
            recommendations.append("⚠️ High number of active sequences - monitor system performance")
        
        return recommendations

def print_system_dashboard():
    """Print comprehensive system dashboard"""
    dashboard = SequenceDashboard()
    
    print("🏗️  I3LANI SEQUENCE SYSTEM DASHBOARD")
    print("=" * 50)
    
    # System Overview
    overview = dashboard.show_system_overview()
    print("\n📊 SYSTEM OVERVIEW:")
    if overview:
        stats = overview['overview']
        print(f"   Total Sequences: {stats['total_sequences']}")
        print(f"   Active: {stats['active_sequences']}")
        print(f"   Completed: {stats['completed_sequences']}")
        print(f"   Failed: {stats['failed_sequences']}")
        print(f"   Average Progress: {stats['average_progress']}%")
        print(f"   Last Activity: {stats['last_activity']}")
    
    # Stuck Sequences
    stuck = dashboard.find_stuck_sequences()
    if stuck:
        print(f"\n⚠️  STUCK SEQUENCES ({len(stuck)}):")
        for seq in stuck[:5]:  # Show first 5
            print(f"   {seq['sequence_id']} - {seq['type']} - Stuck for {seq['stuck_duration_hours']}h")
    
    # Failed Sequences
    failed = dashboard.find_failed_sequences()
    if failed:
        print(f"\n❌ RECENT FAILURES ({len(failed)}):")
        for seq in failed[:5]:  # Show first 5
            print(f"   {seq['sequence_id']} - {seq['type']} - Failed at {seq['failed_at']}")
    
    # Component Health
    if overview and overview.get('component_health'):
        print(f"\n🔧 COMPONENT HEALTH:")
        for comp in overview['component_health'][:5]:  # Show top 5
            print(f"   {comp['component']}: {comp['success_rate']}% success rate ({comp['total_steps']} steps)")
    
    print("\n✅ Dashboard complete - use sequence_dashboard.py for detailed analysis")

if __name__ == "__main__":
    print_system_dashboard()