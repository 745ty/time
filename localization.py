# Localization Dictionary

TEXTS = {
    "en": {
        "title": "Soul Guardian - Roguelike Prototype",
        "menu_start": "Press ENTER to Start Game",
        "menu_tutorial": "Press T for Tutorial",
        "menu_restart": "Press R to Restart",
        "menu_lang": "Press L to Switch Language (English)",
        "game_over": "GAME OVER",
        "score": "Score: {}",
        "level": "Level: {}",
        "weapon": "Weapon: {}",
        "skill_ready": "Skill: Ready",
        "skill_cooldown": "Skill: {}s",
        "tut_move": "Use W, A, S, D to Move",
        "tut_shoot": "Use Mouse to Aim and Left Click to Shoot",
        "tut_switch": "Press Q to Switch Weapons",
        "tut_skill": "Press SPACE to Dash (Skill)",
        "tut_dummy": "Defeat the Dummy Enemy!",
        "tut_complete": "Tutorial Complete! Returning to Menu...",
        "level_reached": "Reached Level: {}",
        "restart_prompt": "Press R to Restart",
        "weapon_sword": "Sword",
        "weapon_pistol": "Pistol",
        "weapon_shotgun": "Shotgun",
        "weapon_machinegun": "MachineGun",
    },
    "zh": {
        "title": "灵魂守卫 - Roguelike 原型",
        "menu_start": "按 ENTER 开始游戏",
        "menu_tutorial": "按 T 进入新手教程",
        "menu_restart": "按 R 重新开始",
        "menu_lang": "按 L 切换语言 (中文)",
        "game_over": "游戏结束",
        "score": "分数: {}",
        "level": "层数: {}",
        "weapon": "武器: {}",
        "skill_ready": "技能: 就绪",
        "skill_cooldown": "技能: {}秒",
        "tut_move": "使用 W, A, S, D 移动",
        "tut_shoot": "使用鼠标瞄准，左键射击",
        "tut_switch": "按 Q 切换武器",
        "tut_skill": "按 SPACE (空格) 冲刺",
        "tut_dummy": "击败木桩敌人！",
        "tut_complete": "教程完成！正在返回菜单...",
        "level_reached": "到达层数: {}",
        "restart_prompt": "按 R 重新开始",
        "weapon_sword": "长剑",
        "weapon_pistol": "手枪",
        "weapon_shotgun": "散弹枪",
        "weapon_machinegun": "机枪",
    }
}

def get_text(key, lang="en", *args):
    text = TEXTS.get(lang, TEXTS["en"]).get(key, key)
    if args:
        return text.format(*args)
    return text
