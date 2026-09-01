"""
backend/content_ranker.py
Layer 2 — Adaptive Content Ranker for SmartSession.
Re-ranks candidate content items based on session intent (Act vs Browse Mode).
Computes Kendall Tau distance (diff_score) comparing standard vs adaptive rankings for split-screen demo.
"""

import copy
import numpy as np

def calculate_kendall_tau_distance(list_a, list_b):
    """Calculates normalized Kendall Tau distance (0.0 to 1.0) between two ordered lists of IDs."""
    if len(list_a) <= 1 or len(list_b) <= 1:
        return 0.0
        
    n = len(list_a)
    pos_b = {item_id: i for i, item_id in enumerate(list_b)}
    
    inversions = 0
    total_pairs = n * (n - 1) // 2
    
    # Count discordant pairs
    for i in range(n):
        for j in range(i + 1, n):
            id_i = list_a[i]
            id_j = list_a[j]
            if id_i in pos_b and id_j in pos_b:
                if pos_b[id_i] > pos_b[id_j]:
                    inversions += 1
                    
    if total_pairs == 0:
        return 0.0
    return round(float(inversions / total_pairs), 4)

def rank_content(intent_label, content_list):
    """
    Ranks content based on intent_label.
    - Act Mode: relevance_score DESC, tap_to_action ASC
    - Browse Mode: discovery_score DESC, content_depth DESC
    """
    standard_ranking = copy.deepcopy(content_list)
    smart_ranking = copy.deepcopy(content_list)
    
    intent_norm = str(intent_label).lower().strip()
    
    if intent_norm == 'act':
        for item in smart_ranking:
            rel = float(item.get('relevance_score', 0.5))
            steps = int(item.get('tap_to_action', 3))
            # Act Rank Score: higher relevance, fewer steps
            step_score = (6.0 - steps) / 5.0
            act_score = (rel * 0.7) + (step_score * 0.3)
            item['composite_score'] = round(act_score, 4)
            item['rank_reason'] = f"High relevance ({int(rel*100)}%) + Direct path ({steps} step{'s' if steps > 1 else ''})"
            
        smart_ranking.sort(key=lambda x: (-x['relevance_score'], x['tap_to_action']))
        
    else: # browse mode default
        for item in smart_ranking:
            disc = float(item.get('discovery_score', 0.5))
            depth = int(item.get('content_depth', 3))
            depth_score = depth / 5.0
            browse_score = (disc * 0.6) + (depth_score * 0.4)
            item['composite_score'] = round(browse_score, 4)
            item['rank_reason'] = f"High discovery value ({int(disc*100)}%) + Rich immersive depth (Level {depth})"
            
        smart_ranking.sort(key=lambda x: (-x['discovery_score'], -x['content_depth']))
        
    # Calculate Kendall Tau normalized distance between standard and smart rankings
    std_ids = [item['content_id'] for item in standard_ranking]
    smart_ids = [item['content_id'] for item in smart_ranking]
    
    diff_score = calculate_kendall_tau_distance(std_ids, smart_ids)
    
    return {
        "standard_ranking": standard_ranking,
        "smart_ranking": smart_ranking,
        "diff_score": diff_score,
        "intent_label": intent_norm
    }

# Default sample content pool for testing and demo initialization
DEFAULT_CONTENT_POOL = [
    {
        "content_id": "c_001",
        "title": "Live Sports Championship Premiere",
        "category": "sports",
        "relevance_score": 0.95,
        "discovery_score": 0.60,
        "tap_to_action": 1,
        "content_depth": 2,
        "thumbnail": "🏆",
        "description": "Watch live HD stream immediately with 1-click action."
    },
    {
        "content_id": "c_002",
        "title": "Cyberpunk Odyssey RPG Launch",
        "category": "game",
        "relevance_score": 0.88,
        "discovery_score": 0.85,
        "tap_to_action": 2,
        "content_depth": 5,
        "thumbnail": "🎮",
        "description": "Explore immersive open world, lore, and gameplay trailers."
    },
    {
        "content_id": "c_003",
        "title": "Indie Music & Creator Showcase",
        "category": "live",
        "relevance_score": 0.45,
        "discovery_score": 0.98,
        "tap_to_action": 3,
        "content_depth": 4,
        "thumbnail": "🎵",
        "description": "Discover trending indie artists and interactive live sessions."
    },
    {
        "content_id": "c_004",
        "title": "High-Stakes Esports Tournament",
        "category": "sports",
        "relevance_score": 0.91,
        "discovery_score": 0.70,
        "tap_to_action": 1,
        "content_depth": 3,
        "thumbnail": "⚡",
        "description": "Join grand finals stream in 1 click."
    },
    {
        "content_id": "c_005",
        "title": "Interactive Mystery Storybook",
        "category": "interactive",
        "relevance_score": 0.35,
        "discovery_score": 0.92,
        "tap_to_action": 4,
        "content_depth": 5,
        "thumbnail": "📚",
        "description": "Choose your own adventure with multi-branch storylines."
    },
    {
        "content_id": "c_006",
        "title": "Quick Daily Quiz Challenge",
        "category": "game",
        "relevance_score": 0.82,
        "discovery_score": 0.50,
        "tap_to_action": 1,
        "content_depth": 1,
        "thumbnail": "🧠",
        "description": "Instant 60-second trivia battle with live rewards."
    }
]

if __name__ == '__main__':
    act_res = rank_content('act', DEFAULT_CONTENT_POOL)
    print("--- ACT MODE RANKING RESULT ---")
    print(f"Diff Score (Kendall Tau): {act_res['diff_score']}")
    print("Smart Ranking Order:")
    for r in act_res['smart_ranking']:
        print(f"  [{r['content_id']}] {r['title']} | Score: {r['composite_score']} | Reason: {r['rank_reason']}")
        
    browse_res = rank_content('browse', DEFAULT_CONTENT_POOL)
    print("\n--- BROWSE MODE RANKING RESULT ---")
    print(f"Diff Score (Kendall Tau): {browse_res['diff_score']}")
    print("Smart Ranking Order:")
    for r in browse_res['smart_ranking']:
        print(f"  [{r['content_id']}] {r['title']} | Score: {r['composite_score']} | Reason: {r['rank_reason']}")
