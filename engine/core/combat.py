from engine.core.state import GameState, BOARD_COLS
from engine.models.card import Unit

def resolve_combat(gs: GameState):
    for col in range(BOARD_COLS):
        p = gs.player.board[col]
        e = gs.enemy.board[col]
        # build order
        order = []
        if p and p.alive:
            order.append((True, p, e))
        if e and e.alive:
            order.append((False, e, p))
        order.sort(key=lambda t: t[1].spd, reverse=True)

        for is_player, attacker, defender in order:
            if not attacker.alive:
                continue
            if defender and defender.alive:
                defender.take_damage(attacker.atk)
            else:
                if is_player:
                    gs.enemy.hp -= attacker.atk
                else:
                    gs.player.hp -= attacker.atk

        # cleanup
        if p and not p.alive:
            gs.player.board[col] = None
        if e and not e.alive:
            gs.enemy.board[col] = None
