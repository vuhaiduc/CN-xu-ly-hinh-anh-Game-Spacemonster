#!/usr/bin/env python3
"""
🌌 GALACTIC GUARDIAN - TEST SCRIPT
Verifica se todos os problemas foram corrigidos
"""

import sys
import os

print("=" * 60)
print("🔍 VERIFICANDO INTEGRIDADE DO GAME...")
print("=" * 60)

# Test 1: Check imports
print("\n✓ TEST 1: Verificando imports...")
try:
    import pygame
    print("  ✅ pygame OK")
except:
    print("  ❌ pygame NÃO INSTALADO - execute: pip install pygame")

try:
    import cv2
    print("  ✅ cv2 OK")
except:
    print("  ❌ cv2 NÃO INSTALADO - execute: pip install opencv-python")

try:
    import mediapipe
    print("  ✅ mediapipe OK")
except:
    print("  ❌ mediapipe NÃO INSTALADO - execute: pip install mediapipe")

try:
    import numpy
    print("  ✅ numpy OK")
except:
    print("  ❌ numpy NÃO INSTALADO - execute: pip install numpy")

# Test 2: Check Python files
print("\n✓ TEST 2: Verificando arquivos Python...")
files_to_check = [
    "config.py",
    "gesture.py",
    "hand_tracking.py",
    "menu.py",
    "main.py",
    "player.py",
    "enemies.py",
    "boss.py",
    "items.py",
    "effects.py",
    "background.py",
    "level_manager.py",
]

for file in files_to_check:
    if os.path.exists(file):
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} - NÃO ENCONTRADO")

# Test 3: Check key fixes
print("\n✓ TEST 3: Verificando correções críticas...")

# Check menu.py for random import
try:
    with open("menu.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "import random" in content:
            print("  ✅ menu.py: import random OK")
        else:
            print("  ❌ menu.py: import random FALTANDO")
        
        if "def draw_text" in content:
            print("  ✅ menu.py: draw_text() definida")
        else:
            print("  ❌ menu.py: draw_text() FALTANDO")
except Exception as e:
    print(f"  ❌ Erro ao verificar menu.py: {e}")

# Check gesture.py for lift detection
try:
    with open("gesture.py", "r", encoding="utf-8") as f:
        content = f.read()
        if 'return "lift"' in content or "return 'lift'" in content:
            print("  ✅ gesture.py: lift detection OK")
        else:
            print("  ⚠️  gesture.py: lift detection pode estar incorreta")
except Exception as e:
    print(f"  ❌ Erro ao verificar gesture.py: {e}")

# Check hand_tracking.py
try:
    with open("hand_tracking.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "self.current_swipe" in content and "self.current_lift" in content:
            print("  ✅ hand_tracking.py: gesture mapping OK")
        else:
            print("  ❌ hand_tracking.py: gesture mapping pode estar incorreta")
except Exception as e:
    print(f"  ❌ Erro ao verificar hand_tracking.py: {e}")

# Test 4: Try importing modules
print("\n✓ TEST 4: Testando imports de módulos...")
try:
    sys.path.insert(0, os.getcwd())
    import config
    print("  ✅ config.py importa OK")
except Exception as e:
    print(f"  ❌ Erro ao importar config: {e}")

try:
    import gesture
    print("  ✅ gesture.py importa OK")
except Exception as e:
    print(f"  ❌ Erro ao importar gesture: {e}")

try:
    import menu
    print("  ✅ menu.py importa OK")
except Exception as e:
    print(f"  ❌ Erro ao importar menu: {e}")

print("\n" + "=" * 60)
print("✅ VERIFICAÇÃO COMPLETA!")
print("=" * 60)

print("""
📋 PRÓXIMOS PASSOS:

1. Leia os documentos:
   - FIXES_SUMMARY.md (resumo das correções)
   - BUGS_FOUND.md (problemas encontrados)

2. Execute o game:
   python main.py

3. Teste os gestos:
   - Swipe esquerda/direita para navegar
   - Pugno para confirmar no menu
   - Levantar a mão para pular no game

4. Se houver erros, execute:
   pip install -r requirements.txt

---
Divirta-se com Galactic Guardian! 🌌
""")
