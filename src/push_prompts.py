"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> int:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        0 se sucesso, 1 se erro
    """
    # Obter username do ambiente
    username = os.getenv('USERNAME_LANGSMITH_HUB')
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurado no .env")
        return 1

    # Construir ChatPromptTemplate
    template = ChatPromptTemplate.from_messages([
        ("system", prompt_data['system_prompt']),
        ("human", prompt_data['user_prompt'])
    ])

    # Preparar metadados
    tags = prompt_data.get('tags', [])
    techniques = prompt_data.get('techniques_applied', [])

    # Combinar tags com técnicas
    all_tags = tags + [f"technique:{t.lower().replace(' ', '-')}" for t in techniques]

    description = prompt_data.get('description', '')

    # Criar README com informações detalhadas
    readme = f"""# {prompt_name}

{description}

## Técnicas Aplicadas
{chr(10).join(f'- {t}' for t in techniques)}

## Versão
{prompt_data.get('version', 'v2')}
"""

    # Fazer push usando LangSmith Client
    client = Client()
    full_prompt_name = f"{username}/{prompt_name}"

    try:
        print(f"📤 Fazendo push para: {full_prompt_name}")

        url = client.push_prompt(
            prompt_identifier=full_prompt_name,
            object=template,
            is_public=True,
            description=description,
            readme=readme,
            tags=all_tags
        )

        print(f"✅ Prompt publicado com sucesso!")
        print(f"   URL: {url}")
        return 0

    except Exception as e:
        print(f"❌ Erro ao fazer push: {e}")
        print("\nVerifique se:")
        print("  1. LANGSMITH_API_KEY está correta no .env")
        print("  2. Você tem permissão para publicar prompts")
        print("  3. O nome do prompt é válido")
        return 1


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    # Reutilizar validação existente
    is_valid, errors = validate_prompt_structure(prompt_data)

    # Validações adicionais para push
    if 'user_prompt' not in prompt_data:
        errors.append("Campo 'user_prompt' é obrigatório")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    # Cabeçalho
    print_section_header("📤 PUSH DE PROMPTS OTIMIZADOS PARA LANGSMITH HUB", char="=", width=70)

    # Verificar variáveis de ambiente
    required_vars = ['LANGSMITH_API_KEY', 'USERNAME_LANGSMITH_HUB']
    if not check_env_vars(required_vars):
        return 1

    # Carregar arquivo YAML
    yaml_path = "prompts/bug_to_user_story_v2.yml"
    print(f"📂 Carregando prompts de: {yaml_path}")

    prompts = load_yaml(yaml_path)
    if not prompts:
        print(f"❌ Não foi possível carregar {yaml_path}")
        return 1

    # Extrair dados do prompt
    prompt_name = list(prompts.keys())[0]
    prompt_data = prompts[prompt_name]

    print(f"\n📝 Prompt: {prompt_name}")
    print(f"   Descrição: {prompt_data.get('description', 'N/A')}")
    print(f"   Versão: {prompt_data.get('version', 'N/A')}")
    print(f"   Técnicas: {len(prompt_data.get('techniques_applied', []))}")

    # Validar prompt
    print("\n🔍 Validando prompt...")
    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("✅ Prompt válido!")

    # Alerta de visibilidade pública
    username = os.getenv('USERNAME_LANGSMITH_HUB')
    print("\n⚠️  ATENÇÃO: Prompt será PÚBLICO no LangSmith Hub")
    print(f"   Nome: {username}/{prompt_name}")

    # Push do prompt
    result = push_prompt_to_langsmith(prompt_name, prompt_data)

    # Mensagem final
    if result == 0:
        print("\n" + "=" * 70)
        print("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        print("\nPróximos passos:")
        print("  1. Verifique: https://smith.langchain.com/prompts")
        print("  2. Execute: python src/evaluate.py")
    else:
        print("\n" + "=" * 70)
        print("❌ PROCESSO FINALIZADO COM ERROS")
        print("=" * 70)

    return result


if __name__ == "__main__":
    sys.exit(main())
