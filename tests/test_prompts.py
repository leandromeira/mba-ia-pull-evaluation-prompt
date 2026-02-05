"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def prompt_data():
    """Fixture que carrega os dados do prompt."""
    data = load_prompts(PROMPT_FILE)
    # O YAML tem a estrutura: { "bug_to_user_story_v2": { ... } }
    prompt_key = list(data.keys())[0]
    return data[prompt_key]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado no prompt"
        assert prompt_data["system_prompt"] is not None, "Campo 'system_prompt' está None"
        assert len(prompt_data["system_prompt"].strip()) > 0, "Campo 'system_prompt' está vazio"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        system_prompt = prompt_data.get("system_prompt", "")
        
        # Verificar se contém definição de papel/persona
        role_indicators = [
            "você é",
            "voce é", 
            "você é um",
            "voce é um",
            "atue como",
            "seu papel",
            "sua função",
            "# PAPEL",
            "## PAPEL",
            "role:",
            "persona:"
        ]
        
        system_prompt_lower = system_prompt.lower()
        has_role = any(indicator.lower() in system_prompt_lower for indicator in role_indicators)
        
        assert has_role, "O prompt não define uma persona/papel. Adicione 'Você é um...' ou '# PAPEL'"

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")
        full_prompt = system_prompt + " " + user_prompt
        
        format_indicators = [
            "user story",
            "user-story",
            "como um",
            "como o",
            "eu quero",
            "para que",
            "critérios de aceitação",
            "dado que",
            "quando",
            "então",
            "markdown",
            "formato",
            "estrutura"
        ]
        
        full_prompt_lower = full_prompt.lower()
        has_format = any(indicator in full_prompt_lower for indicator in format_indicators)
        
        assert has_format, "O prompt não menciona formato User Story ou Markdown"

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data.get("system_prompt", "")
        
        # Verificar se contém exemplos
        example_indicators = [
            "exemplo",
            "example",
            "## exemplo",
            "### exemplo",
            "bug:",
            "---",  # Separadores de exemplos
            "entrada:",
            "saída:"
        ]
        
        system_prompt_lower = system_prompt.lower()
        has_examples = any(indicator.lower() in system_prompt_lower for indicator in example_indicators)
        
        # Também verificar se há múltiplos exemplos (contando ocorrências de "Exemplo")
        example_count = system_prompt_lower.count("exemplo")
        
        assert has_examples, "O prompt não contém exemplos few-shot. Adicione exemplos de entrada/saída"
        assert example_count >= 2, f"O prompt deve ter pelo menos 2 exemplos few-shot. Encontrados: {example_count}"

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum '[TODO]' no texto."""
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")
        description = prompt_data.get("description", "")
        
        full_content = system_prompt + " " + user_prompt + " " + description
        full_content_upper = full_content.upper()
        
        # Verificar por TODO em diferentes formatos
        todo_patterns = [
            "[TODO]",
            "[ TODO ]",
            "TODO:",
            "# TODO",
            "// TODO",
            "/* TODO"
        ]
        
        for pattern in todo_patterns:
            assert pattern not in full_content_upper, f"Encontrado '{pattern}' no prompt. Remova antes de enviar."

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        
        assert techniques is not None, "Campo 'techniques_applied' não encontrado no prompt"
        assert isinstance(techniques, list), "Campo 'techniques_applied' deve ser uma lista"
        assert len(techniques) >= 2, f"O prompt deve listar pelo menos 2 técnicas. Encontradas: {len(techniques)}"
        
        # Verificar se as técnicas são válidas
        valid_techniques = [
            "few_shot",
            "few-shot",
            "chain_of_thought",
            "chain-of-thought",
            "cot",
            "tree_of_thought",
            "skeleton_of_thought",
            "react",
            "role_prompting",
            "role-prompting",
            "rubric_based",
            "output_format",
            "complexity_classification"
        ]
        
        for technique in techniques:
            technique_lower = technique.lower().replace(" ", "_").replace("-", "_")
            is_valid = any(valid in technique_lower for valid in [t.replace("-", "_") for t in valid_techniques])
            assert is_valid, f"Técnica '{technique}' não é reconhecida. Use técnicas válidas como: {valid_techniques}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])