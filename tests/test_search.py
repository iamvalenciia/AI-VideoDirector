#!/usr/bin/env python
"""
Script de prueba para verificar que DuckDuckGo funciona correctamente
y está devolviendo resultados actuales.
"""

from datetime import datetime

from langchain_community.tools import DuckDuckGoSearchRun


def test_duckduckgo_search():
    """
    Prueba si DuckDuckGo está funcionando y devuelve resultados recientes.
    """
    print("=" * 60)
    print("🧪 TESTING DUCKDUCKGO SEARCH TOOL")
    print("=" * 60)
    print(f"\n📅 Current date: {datetime.now().strftime('%Y-%m-%d')}\n")

    # Lista de queries de prueba
    test_queries = [
        "cryptocurrency news today",
        "Bitcoin latest 2025",
        "Ethereum breaking news",
    ]

    search = DuckDuckGoSearchRun()

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 60}")
        print(f"Test {i}/3: Searching for '{query}'")
        print("=" * 60)

        try:
            result = search.run(query)

            # Verificar si hay resultados
            if result and len(result) > 50:  # Al menos 50 caracteres
                print("✅ SUCCESS: Got results from DuckDuckGo")
                print(f"\nFirst 500 characters of result:\n{'-' * 60}")
                print(result[:500])
                print(f"{'-' * 60}\n")

                # Verificar si menciona años recientes
                if "2025" in result or "2024" in result:
                    print("✅ GOOD: Results mention recent years (2024/2025)")
                elif "2023" in result:
                    print("⚠️  WARNING: Results mention 2023 (might be outdated)")
                else:
                    print("⚠️  WARNING: No clear date mentions in results")

            else:
                print("❌ FAILED: No results or results too short")
                print(f"Result: {result}")

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

    print(f"\n{'=' * 60}")
    print("🏁 TESTING COMPLETE")
    print("=" * 60)
    print("\nIf you see ✅ SUCCESS and recent dates, DuckDuckGo is working!")
    print("If you see errors or old dates, there's a problem to fix.\n")


if __name__ == "__main__":
    test_duckduckgo_search()
