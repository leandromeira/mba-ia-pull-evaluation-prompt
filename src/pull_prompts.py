"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt do LangSmith Hub e salva localmente.

    Returns:
        0 se sucesso, 1 se erro
    """
    print_section_header("🔄 Pull de Prompts do LangSmith Hub")

    # Verificar credenciais
    required_vars = ['LANGSMITH_API_KEY']
    if not check_env_vars(required_vars):
        return 1

    prompt_id = "leonanluppi/bug_to_user_story_v1"

    try:
        print(f"📥 Fazendo pull do prompt: {prompt_id}")
        prompt = hub.pull(prompt_id)

        print(f"✅ Prompt baixado com sucesso!")

        # Extrair informações do prompt
        prompt_data = {
            'prompt_id': prompt_id,
            'prompt_template': prompt.messages[0].prompt.template if hasattr(prompt, 'messages') else str(prompt),
            'input_variables': prompt.input_variables if hasattr(prompt, 'input_variables') else [],
            'metadata': {
                'source': 'langsmith_hub',
                'pulled_at': None  # Será preenchido quando implementarmos timestamp
            }
        }

        # Salvar localmente
        output_path = "prompts/raw_prompts.yml"
        print(f"💾 Salvando em: {output_path}")

        if save_yaml(prompt_data, output_path):
            print(f"✅ Prompt salvo com sucesso em {output_path}")
            return 0
        else:
            print(f"❌ Erro ao salvar prompt")
            return 1

    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        print("\nVerifique se:")
        print("  1. A LANGSMITH_API_KEY está correta no .env")
        print(f"  2. O prompt '{prompt_id}' existe no LangSmith Hub")
        print("  3. Você tem permissão para acessar este prompt")
        return 1


def main():
    """Função principal"""
    print("🚀 Iniciando pull de prompts do LangSmith")
    print("-" * 50)

    result = pull_prompts_from_langsmith()

    if result == 0:
        print("\n" + "=" * 50)
        print("✅ Processo concluído com sucesso!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ Processo finalizado com erros")
        print("=" * 50)

    return result


if __name__ == "__main__":
    sys.exit(main())
